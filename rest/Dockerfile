FROM python:3.8

ADD rest-server.py /

RUN pip3 install --upgrade pandas pika jsonpickle requests flask img2pdf cassandra-driver astrapy flask-cors flask-jwt-extended google-api-core google-api-python-client google-auth google-auth-httplib2 google-cloud google-cloud-core google-cloud-storage google-cloud-vision jsonify pillow 

CMD mkdir /app
WORKDIR /app

COPY . /app

EXPOSE 5000
CMD cd /app && python3 rest-server.py