from celery import Celery
from datetime import datetime

from zipfile import ZipFile
import bz2, gzip
import os, sys
import requests
import re

from google.cloud import storage

# celery = Celery('tasks', broker="redis://redis:6379/0")
celery = Celery('tasks', broker="redis://:redisultramegasecurepassword@10.0.0.37:6379/0")

client = storage.Client.from_service_account_json('/home/juliethquinchia/proyecto-software-en-la-nube-4692a4693e31.json')
bucket = client.bucket('bucket-flask-app')


FILE_PATH = '/nfs/general/'

puerto = os.environ.get('URL_MAQUINA_VIRTUAL')

@celery.task(name="registrar_log")
def registrar_log(usuario, fecha):
    with open('conversion_api/mensajeria/log_signin.txt','a+') as file:
        file.write('{} - Inicio de sesión:{}\n'.format(usuario, fecha))

@celery.task(name="process_files")
def process_files(task):
    format_to_convert = task['new_format']
    origin_file = task['file_name']
    
    print('/api/process/'+task['id'])
    blob = bucket.blob(origin_file)
    blob.download_to_filename(origin_file)
    
    if format_to_convert == 'tarbz2' or format_to_convert == 'tar.bz2' or format_to_convert == 'bz2':
        convert_to_bz2(origin_file)    
        x = requests.get('/api/process/'+task['id'])
      
    elif format_to_convert == 'zip':
        convert_to_zip(origin_file)
        x = requests.get('/api/process/'+task['id'])
  
    elif format_to_convert == 'tar.gz' or format_to_convert == 'gz' or format_to_convert == 'targz':
        convert_to_gz(origin_file)
        x = requests.get('/api/process/'+task['id'])
       
    else:
        print('not supported format?')

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
    print(__file__)
    
    input_file = open(filename, "rb")
    output_file = open(filename + '.bz2', "wb")
    output_file.write(bz2.compress(input_file.read()))
    
    upload_file(filename + '.bz2')

    output_file.close()
    input_file.close()