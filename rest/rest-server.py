##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
import hashlib
import json
import pickle
from PIL import Image
import img2pdf
import google.auth
import google.oauth2.service_account as service_account
from google.oauth2.service_account import Credentials
from google.cloud import vision
from google.cloud import storage
import uuid
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import datetime
import time
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, BatchStatement
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy
from cassandra.query import tuple_factory
import pika
import re
import pandas as pd

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

#cluster = Cluster(['127.0.0.1'],port=9042) or Cluster(['127.0.0.1'],port=7000) or Cluster(['127.0.0.1'],port=7001) or Cluster(['127.0.0.1'],port=9160) or Cluster(['127.0.0.1'],port=7199)
cluster = Cluster(['127.0.0.1'],port=9042)
session = cluster.connect('test1')
app.config["JWT_SECRET_KEY"] = "hvhvgcgc675765bhbj"  # Change this!
jwt = JWTManager(app)

credential_path = "keyFile-credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print("Connecting to rabbitmq({})".format(rabbitMQHost))


def insert_customer(customer_data):
  try:
    #session = cluster.connect('test1')
    username = customer_data['username']
    email = customer_data['email']
    password = customer_data['password']
    print(username, email , password)
    stmt = session.prepare('INSERT INTO customer (username,email,password) '
                            'VALUES (?, ?, ?)'
                           'IF NOT EXISTS')
    results = session.execute(stmt, [ customer_data['username'], customer_data['email'], customer_data['password'] ])
    print("done session")

  except Exception as e:
    enqueueDataToLogsExchange("Exception occured" + str(e),"debug")
    print("Exception occured" + str(e))
  return customer_data


def search_customer(customer_data):
  try:
    #session = cluster.connect('test1')
    print(customer_data)
    msg =''
    email = customer_data['username']
    #email = customer_data['email']
    password = customer_data['password']
    print(email , password)
    query = "select * from customer where email='"+ email + "' and password='" + password+ "' ALLOW FILTERING;"
    print(query)
    rows = session.execute(query)
    print(type(rows))
    c = 0
    for i in rows:
        c+=1
    print(c)
    print("done session")
      # If account exists in accounts table in out database
    if c > 0:
        print("done resultset")
        print("Logged in successfully!")
        return customer_data
    else:
            # Account doesnt exist or username/password incorrect
         msg = 'Incorrect username/password!'
         print(msg)
         return msg
         
  except Exception as e:
    enqueueDataToLogsExchange("Exception occured" + str(e),"debug")
    print("Exception occured" + str(e))


def insert_expense(user_details,timestamp,billvalue,category,totalvalue,month):
    query = session.prepare('INSERT INTO expense(email,timestamp, bill_value, category,final_value,month)'
                            'VALUES (?, ?, ?, ?, ?, ?)'
                           'IF NOT EXISTS')
    results = session.execute(query, [user_details,timestamp,billvalue,category,totalvalue,month])
    print('Insert worked!')


def final_value(user_details,timestamp,billvalue,category,month):
    totalvalue = 0
    print('It works!')
    df = pd.DataFrame()
    query = "select final_value from expense where email='"+str(user_details)+ "' limit 1 allow filtering;"
    rows = session.execute(query)
    df = df.append(pd.DataFrame(rows,index=[0]))
    try:
        float(billvalue)
        if(df.empty==True):
            totalvalue = float(billvalue)
            print(totalvalue)
            insert_expense(user_details,str(timestamp),billvalue,category,str(totalvalue),str(month))
            print("If no prev entry for email works!")    
        else:
            totalvalue = str(df['final_value'])
            totalvalue = totalvalue[1:].strip().split('\n')[0]
            print("Total of previous is:" + totalvalue)
            totalvalue = float(billvalue) + float(totalvalue)                                          
            insert_expense(user_details,str(timestamp),billvalue,category,str(totalvalue),str(month))
            print("Prev entry for email works!")  
    except:
        billvalue = ''
        query = "select final_value from expense limit 1 allow filtering;"
        rows = session.execute(query)
        df = df.append(pd.DataFrame(rows,index=[0]))   
        if(df.empty==True):
            totalvalue = ''
    return str(totalvalue)

def get_timestamp(email,month):
    try:
        session = cluster.connect('test1')
        msg =''
        print(email, month)
        query = "select timestamp from expense where email='"+str(email)+"' and month='"+str(month)+"'ALLOW FILTERING;"
        df = pd.DataFrame()
        timestamps = []
        for row in session.execute(query):
            df = df.append(pd.DataFrame(row,index=[0]))
        df.columns=['timestamp']
        timestamps = df['timestamp'].to_list()
        print(timestamps)
        return timestamps
    except Exception as e: 
        enqueueDataToLogsExchange("Exception occured" + str(e),"debug")
        print("Exception occured " + str(e))

def search_expenses(email,month,category):
  try:
    session = cluster.connect('test1')
    print(email , category, month)
    query = "select bill_value from expense where email='"+ str(email) + "' and category='" + str(category)+ "' and month='" + str(month)+ "' ALLOW FILTERING;"
    #print(query)
    df = pd.DataFrame()
    setfinal = []
    for row in session.execute(query):
        df = df.append(pd.DataFrame(row,index=[0]))
    if(df.empty!=True):
        df.columns=['bill_value']
        setfinal = df['bill_value'].to_list()
        #print(setfinal,type(setfinal))
        sum = 0
        for i in setfinal:
            sum+=float(i)
        print('Sum acc to category is: ',sum)
        return str(sum)
    else:
        return "N/A"
        
  except Exception as e:
    enqueueDataToLogsExchange("Exception occured" + str(e),"debug")
    print("Exception occured " + str(e))



def enqueueDataToLogsExchange(message,messageType):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

    infoKey = f"{platform.node()}.rest.info"
    debugKey = f"{platform.node()}.rest.debug"

    if messageType == "info":
        key = infoKey
    elif messageType == "debug":
        key = debugKey

    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key='logs', body=json.dumps(message))

    print(" [x] Sent %r:%r" % (key, message))

    rabbitMQChannel.close()
    rabbitMQ.close()



class enqueueWorker(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.onResponse,
            auto_ack=True)
    
    def onResponse(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    # Producer is rest-server and sending data to RabbitMQ Queue 'toWorkerQueue' ie Consumer is worker-server
    def enqueueDataToWorker(self,message):
        self.response = None
        self.corr_id = str(uuid.uuid4())    
        self.channel.basic_publish(
            exchange='', routing_key='toWorkerQueue',properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ), 
            body=json.dumps(message))
        while self.response is None:
            self.connection.process_data_events()
        #print(self.response)        
        return str(self.response.decode('utf-8'))
        #return Response(response=json.dumps(self.response), status=200, mimetype="application/json")
        #print(" [x] Sent %r:%r" % ('toWorker', message))



@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        # enqueueDataToLogsExchange('Into fetch prices api',"info")
        data = request.get_json()
        print("-------Data-------" + str(data))
        response = insert_customer(data)
        enqueueDataToLogsExchange('Call to api /api/auth/signup','info')

        # enqueueDataToLogsExchange('Fetch prices api executed succesfully',"info")
        return Response(response=json.dumps(response), status=200, mimetype="application/json")
        
    except Exception as e:
        enqueueDataToLogsExchange('Error occured in api /api/auth/signup','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")


@app.route('/api/auth/signin', methods=['POST'])
def signin():
    try:
        # enqueueDataToLogsExchange('Into fetch prices api',"info")
        data = request.get_json()
        print("-------Data-------" + str(data))
        email = request.json.get("username",None)
        password = request.json.get("password",None)
        enqueueDataToLogsExchange('Call to api /api/auth/signin','info')

        #calling db function
        response = search_customer(data)
        #print(response)    
        if response != 'Incorrect username/password!':
            print("hi")
            access_token = create_access_token(identity=email)
            #print(access_token)
        response.update({'accessToken': access_token})
        # enqueueDataToLogsExchange('Fetch prices api executed succesfully',"info")
        print("Response:")
        print(response)
        return Response(response=json.dumps(response), status=200, mimetype="application/json")
        #return make_response(jsonify(response=response), 201)
        
    except Exception as e:
        enqueueDataToLogsExchange('Error occured in api /api/auth/signin','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")


@app.route('/api/upload', methods=['POST'])
def handle_form():
    try:
        category = request.form['category']
        print(category)
        user_details = request.form['username']
        print(user_details)
        timestamp = str(datetime.utcnow())
        m = datetime.utcnow().date()
        month = str(m)
        month = month.split('-')[1]
        enqueueDataToLogsExchange('Call to api /api/upload','info')
        print("Posted file: {}".format(request.files['file']))
        file1 = request.files['file'].read()
        print(type(file1))
        ext = request.files['file'].filename.split('.')[-1]
        #ext = 'jpg'
        name = str(user_details)+"_"+str(timestamp)+'.'+str(ext)
        f = open(name,'w+b')
        f.write(file1)
        f.close()    
        name2 = str(user_details)+"_"+str(timestamp)+'.pdf'
        if str(ext)=='jpg' or str(ext)=='jpeg' or str(ext)=='png':
            image = Image.open(name)
            # converting into chunks using img2pdf
            pdf_bytes = img2pdf.convert(image.filename)
            # # opening or creating pdf file
            #name2 = str(user_details)+"_"+str(timestamp)+'.pdf'
            file = open(name2, 'w+b')
            # # writing pdf files with chunks
            file.write(pdf_bytes)
            # # closing image file
            image.close()
            # # closing pdf file
            file.close()
            # # output
            print("Successfully made pdf file")
            #print(type(file1))
        client = storage.Client()
        BUCKET_NAME = 'projectexpensegenerator'
        bucket = client.get_bucket(BUCKET_NAME)
        destination_blob_name = name2
        blob1 = bucket.blob(destination_blob_name)
        blob1.upload_from_filename(name2)
        # print("File {} uploaded to {}.".format(f, destination_blob_name))
        # blobs = bucket.list_blobs()
        # for blob2 in blobs: 
        #     num = blob2.name.count('/')
        #     string = blob2.name.split('/')[num]
        #     if string != "":
        #         print(string)

        data = {'user_details':user_details,'timestamp':timestamp,'category':category}
        
        dataToWorker = enqueueWorker()
        response1 = dataToWorker.enqueueDataToWorker(data)
        print(response1)
        billvalue = re.sub('[^\d\.]', '',response1)
        total_value = final_value(user_details,timestamp,billvalue,category,month)
        response = {'category':category,'bill_value':str(billvalue),'total_value':str(total_value)}
        return Response(response=json.dumps(response), status=200, mimetype="application/json")

    except Exception as e:
        print("Something went wrong" + str(e))
        enqueueDataToLogsExchange('Error occured in api /api/upload','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")


@app.route('/api/auth/getpdf', methods=['POST'])
def get_pdf():
    data = request.get_json()
    print("-------Data-------" + str(data))
    email = request.json.get("username",None)
    month = request.json.get("month",None)
    #response = search_(category,username)
    #response1 = 565
    #total_value = ''
    response = {'month':str(month),'email':str(email)}
    timestamps = []
    timestamps = get_timestamp(email,month)
    print(timestamps)
    #insert_expense(user_details,category,timestamp,response1)
    
    return Response(response=json.dumps(response), status=200, mimetype="application/json")
    #return ""


@app.route('/api/auth/getexpenses', methods=['POST'])
def get_expenses():
    data = request.get_json()
    print("-------Data-------" + str(data))
    email = request.json.get("username",None)
    month = request.json.get("month",None)
    category = request.json.get("category",None)
    enqueueDataToLogsExchange('Call to api /api/auth/getexpenses','info')

    response = search_expenses(email,month,category)
    #response1 = 565
    #total_value = ''

    #response = {'month':str(month),'email':str(email),'category':category}
    #insert_expense(user_details,category,timestamp,response1)
    
    return Response(response=json.dumps(response), status=200, mimetype="application/json")
    #return ""



# start flask app
app.run(host="0.0.0.0", port=5000,debug=True)
