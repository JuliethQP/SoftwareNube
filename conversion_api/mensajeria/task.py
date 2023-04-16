from apirest.models import Task as files
from celery import Celery
from datetime import datetime

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(name="registrar_log")
def registrar_log(usuario, fecha):
    with open('log_signin.txt','a') as file:
        file.write('{} - Inicio de sesión:{}\n'.format(usuario, fecha))

@celery.task(name="process_files")
def process_files(file_id):
    file = files.query.get(file_id)
    print('INIT PROCESS')
    with open('log_mq.txt','a') as file:
        file.write('{} - Process file:\n'.format(file.file_name))

    print(file)