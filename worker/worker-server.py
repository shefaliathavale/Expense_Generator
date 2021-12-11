#
# Worker server
#
import pickle
import platform
import io
import os
import sys
import pika
import redis
import hashlib
import json
import requests
import re
from google.cloud import vision
from google.cloud import storage
import img2pdf
from PIL import Image
import google.auth
import google.oauth2.service_account as service_account
import uuid

# hostname = platform.node()
## Configure test vs. production
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print(f"Connecting to rabbitmq({rabbitMQHost})")

## Set up rabbitmq connection
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
toWorkerResult = rabbitMQChannel.queue_declare(queue='toWorkerQueue')

credential_path = "keyFile-credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


def enqueueDataToLogsExchange(message,messageType):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

    infoKey = f"{platform.node()}.worker.info"
    debugKey = f"{platform.node()}.worker.debug"

    if messageType == "info":
        key = infoKey
    elif messageType == "debug":
        key = debugKey

    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key='logs', body=json.dumps(message))

    print(" [x] Sent %r:%r" % (key, message))

    rabbitMQChannel.close()
    rabbitMQ.close()


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body}", file=sys.stdout, flush=True)
    queuedata = json.loads(body)
    print(queuedata)
    #file = queuedata['file']
    timestamp = queuedata['timestamp']
    user_details = queuedata['user_details']
    category = queuedata['category']
    print(timestamp,user_details,category)
    enqueueDataToLogsExchange('Worker processing sentences','info')

    gcs_source_uri = 'gs://projectexpensegenerator/'+str(user_details)+'_'+str(timestamp)+'.pdf'
    gcs_destination_uri = 'gs://projectexpensegeneratorjson/'+str(user_details)+'_'+str(timestamp)
    print(gcs_source_uri,gcs_destination_uri)

    detect_document(gcs_source_uri,gcs_destination_uri)
    response = json_to_text(gcs_destination_uri)
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id = properties.correlation_id), body=str(response))
    
    ch.basic_ack(delivery_tag=method.delivery_tag)


def detect_document(gcs_source_uri,gcs_destination_uri):
    mime_type = 'application/pdf'
    batch_size = 5
    client = vision.ImageAnnotatorClient()
    feature = vision.Feature(type_ = vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source,mime_type=mime_type)
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(gcs_destination=gcs_destination,batch_size=batch_size)
    async_request = vision.AsyncAnnotateFileRequest(features=[feature],input_config=input_config,output_config=output_config)
    operation = client.async_batch_annotate_files(requests=[async_request])
    print("Waiting for the operation to finish")
    operation.result(timeout=420)


def json_to_text(gcs_destination_uri):
    storage_client = storage.Client()
    match = re.match(r'gs://([^/]+)/(.+)',gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    bucket = storage_client.get_bucket(bucket_name)
    blob_list = list(bucket.list_blobs(prefix=prefix))
    # print('\nOutput Files:')
    # for blob in blob_list:
    #     print(blob.name)
    for n in range(len(blob_list)):     
        output = blob_list[n]     
        json_string = output.download_as_string()
        response = json.loads(json_string)
        file = open("batch{}.txt".format(str(n)),"w")  
        for m in range(len(response['responses'])):
            first_page_response = response['responses'][m]
            annotation = first_page_response['fullTextAnnotation']      
            print("Full Text:\n")
            print()
            print(annotation['text']) 
            file.write(annotation['text'])
        str1 = repr(annotation['text'])
        m = str1.split('\\n')
        str2 = ["total","amount"]
        dict1 = {}
        c = 0
        for i in range(len(m)):
            for j in range(len(str2)):
                c = m[i].lower()
                if str2[j] in c:
                    dict1[m[i]] = m[i+1]
        print(dict1)
        key1 = 0
        if(list(dict1)[-1]):    
            key1 = list(dict1)[-1]
        bill_value = dict1[key1]
        print("Total Bill Value is: ", bill_value)
        return bill_value
    # enqueueDataToLogsExchange('Worker processing sentences','info')    
    sys.stdout.flush()
    sys.stderr.flush()
    # enqueueDataToLogsExchange('Sentences processed and added into database','info')

print("Waiting for messages:")
rabbitMQChannel.basic_qos(prefetch_count=1)
rabbitMQChannel.basic_consume(queue='toWorkerQueue', on_message_callback=callback)
rabbitMQChannel.start_consuming()
