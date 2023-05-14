from flask import Flask
from datetime import timedelta
import os
from google.oauth2 import service_account
from google.cloud.sql.connector import Connector, IPTypes
from apirest.task import proccessFileTask

credential_path = "/home/juliethquinchia/proyecto-software-en-la-nube-906bd5b19e9e.json"
#credential_path = "google/proyecto-software-en-la-nube-906bd5b19e9e.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def getconn():
    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
    with Connector() as connector:
        conn = connector.connect(
            "proyecto-software-en-la-nube:us-central1:conversor-db", # Cloud SQL Instance Connection Name
            "pg8000",
            user="postgres",
            password="admin",
            db="postgres",
            ip_type=ip_type
        )
        return conn

def create_app(config_name):
    app = Flask(__name__)  

    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "creator": getconn}
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversion_api.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'frase-secreta'
        app.config['PROPAGATE_EXCEPTIONS']=True
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
        puerto = os.environ.get('URL_MAQUINA_VIRTUAL')
        print('---el puerto es',puerto)
        print('---Inicio API')
        
        proccessFileTask()
    return app
