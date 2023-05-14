from zipfile import ZipFile
from flask import current_app
import bz2, gzip
import time
import json
import os

from .models import db, Task
from google.cloud import storage, pubsub_v1
from google.cloud.pubsub_v1.types import PullRequest

client = storage.Client.from_service_account_json('/home/juliethquinchia/proyecto-software-en-la-nube-906bd5b19e9e.json')
#client = storage.Client.from_service_account_json('google/proyecto-software-en-la-nube-906bd5b19e9e.json')
bucket = client.bucket('bucket-flask-app')
from flask import current_app

FILE_PATH = '/nfs/general/'

puerto = os.environ.get('URL_BALANCEADOR_DE_CARGA')

project_id = "proyecto-software-en-la-nube"
subscription_name = "suscripcion-proyecto-conversor-001"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)


def upload_file(filename):
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)

def verify_path():
    if 'files' in os.getcwd():
        print(os.getcwd())
    else:
        file_path = '/nfs/general/' 
        os.chdir(file_path)
    print(os.getcwd())

def convert_to_zip(filename):
    with ZipFile(filename + ".zip", "w") as f:       
        arcname = filename.replace("\\", "/")     
        arcname = arcname[arcname.rfind("/") + 1:]
        f.write(filename, arcname)        
        upload_file(filename + ".zip")

def convert_to_gz(filename):
    try:
        f = open(filename, "rb")
    except IOError as e:
        print(e.errno, e)
    else:
        data = f.read()
        f.close()

    if data is not None:
        f = gzip.open(filename + ".gz", "wb")      
        f.write(data)
        upload_file(filename + ".gz")
        f.close()

def convert_to_bz2(filename):   
    input_file = open(filename, "rb")
    output_file = open(filename + '.bz2', "wb")
    output_file.write(bz2.compress(input_file.read()))
    
    upload_file(filename + '.bz2')

    output_file.close()
    input_file.close()

def updateTask(filename, newFormat):
    file_path_processed= filename + "." + newFormat
    blob = bucket.blob(file_path_processed)    
    if blob.exists:     
        task = Task.query.filter(Task.file_name == filename).first() 
        print('task--------->',task)
        task.status = 1
        db.session.add(task)
        db.session.commit()
        return True
    else: 
         return False

def proccessFileTask():
    while True:
        pull_request = PullRequest(
            subscription=subscription_path,
            max_messages=1)

        response = subscriber.pull(request=pull_request)
        ack_ids = []
        nack_ids = []

        for received_message in response.received_messages:
            print(f"Mensaje recibido: {received_message.message.data}")

            json_data = json.loads(received_message.message.data)

            format_to_convert = json_data["new_format"]
            origin_file = json_data["filename"]
            
            blob = bucket.blob(origin_file)
            blob.download_to_filename(f'{origin_file}')
        
            if format_to_convert == 'tarbz2' or format_to_convert == 'tar.bz2' or format_to_convert == 'bz2':
                convert_to_bz2(origin_file)          

            elif format_to_convert == 'zip':
                convert_to_zip(origin_file)
    
            elif format_to_convert == 'tar.gz' or format_to_convert == 'gz' or format_to_convert == 'targz':
                convert_to_gz(origin_file)
        
            else:
                print('not supported format?')

            updateResult = updateTask(origin_file, format_to_convert)
            if updateResult:
                ack_ids.append(received_message.ack_id)
            else:
                nack_ids.append(received_message.ack_id)

            os.remove(f'{origin_file}')

        
        if ack_ids:
            subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})

        if nack_ids:
            subscriber.nacknowledge(request={"subscription": subscription_path, "nack_ids": nack_ids})
        
        time.sleep(1)