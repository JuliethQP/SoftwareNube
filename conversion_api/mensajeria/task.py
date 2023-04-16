from celery import Celery
from datetime import datetime

import zipfile
import bz2
import gzip
import os
import sys

celery = Celery('tasks', broker='redis://localhost:6379/0')
FILE_PATH = '/conversion_api/files/'

@celery.task(name="registrar_log")
def registrar_log(usuario, fecha):
    with open('conversion_api/mensajeria/log_signin.txt','a') as file:
        file.write('{} - Inicio de sesión:{}\n'.format(usuario, fecha))

@celery.task(name="process_files")
def process_files(task):
    format_to_convert = task['new_format']
    origin_file = task['file_name']

    filename = origin_file
    print('<?' + format_to_convert + '>' + filename)


    if format_to_convert == 'tarbz2':
        convert_to_bz2(origin_file)
    else:
        print('not supported format?')

    with open('conversion_api/mensajeria/log_mq.txt','a+') as file:
        file.write('{} - Process file:\n'.format(origin_file))

def convert_to_zip(filename):
    with ZipFile(filename + ".zip", "w") as f:
        arcname = filename.replace("\\", "/")
        arcname = arcname[arcname.rfind("/") + 1:]
        f.write(filename, arcname)

def convert_to_gz(filename):
    data = read_file(filename)
    if data is not None:
        f = gzip.open(filename + ".gz", "wb")
        f.write(data)
        f.close()

def convert_to_bz2(filename):
    file_path = os.getcwd() + '/files/' + filename
    print('__file__:    ', file_path)
    
    input_file = open(file_path, "rb")
    output_file = open(file_path + 'bz2', "wb")
    output_file.write(bz2.compress(input_file.read()))

    output_file.close()
    input_file.close()