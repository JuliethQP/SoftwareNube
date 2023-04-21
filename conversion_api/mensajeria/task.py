from celery import Celery
from datetime import datetime

from zipfile import ZipFile
import bz2, gzip
import os, sys
import requests


# celery = Celery('tasks', broker="redis://redis:6379/0")
celery = Celery('tasks', broker="redis://:redisultramegasecurepassword@35.185.127.60:6379")


FILE_PATH = '/conversion_api/files/'

@celery.task(name="registrar_log")
def registrar_log(usuario, fecha):
    with open('conversion_api/mensajeria/log_signin.txt','a+') as file:
        file.write('{} - Inicio de sesión:{}\n'.format(usuario, fecha))

@celery.task(name="process_files")
def process_files(task):
    format_to_convert = task['new_format']
    origin_file = task['file_name']

    filename = origin_file

    if format_to_convert == 'tarbz2' or format_to_convert == 'tar.bz2' or format_to_convert == 'bz2':
        convert_to_bz2(origin_file)
        print('hola')
        x = requests.get('http://localhost:5500/api/process/'+task['id'])
        print(x.status_code)
    elif format_to_convert == 'zip':
        convert_to_zip(origin_file)
        x = requests.get('http://localhost:5500/api/process/'+task['id'])
        print(x.status_code)
    elif format_to_convert == 'tar.gz' or format_to_convert == 'gz' or format_to_convert == 'targz':
        convert_to_gz(origin_file)
        x = requests.get('http://localhost:5500/api/process/'+task['id'])
        print(x.status_code)
    else:
        print('not supported format?')

def verify_path():
    if 'files' in os.getcwd():
        print(os.getcwd())
    else:
        file_path = os.getcwd() + '/files/'
        os.chdir(file_path)
    print(os.getcwd())

def convert_to_zip(filename):
    verify_path()
    with ZipFile(filename + ".zip", "w") as f:
        arcname = filename.replace("\\", "/")
        arcname = arcname[arcname.rfind("/") + 1:]
        f.write(filename, arcname)

def convert_to_gz(filename):
    verify_path()
    try:
        f = open(filename, "rb")
    except IOError as e:
        print(e.errno, e.message)
    else:
        data = f.read()
        f.close()

    if data is not None:
        f = gzip.open(filename + ".gz", "wb")
        f.write(data)
        f.close()

def convert_to_bz2(filename):
    verify_path()
    print(__file__)
    
    input_file = open(filename, "rb")
    output_file = open(filename + '.bz2', "wb")
    output_file.write(bz2.compress(input_file.read()))

    output_file.close()
    input_file.close()