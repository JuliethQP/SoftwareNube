from flask import Flask
from datetime import timedelta
import os
from google.cloud.sql.connector import Connector, IPTypes


credential_path = "/home/juliethquinchia/SoftwareNube/conversion_api/credenciales/proyecto-software-en-la-nube-ec7914a19c66.json"
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
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'frase-secreta'
        app.config['PROPAGATE_EXCEPTIONS']=True
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  
        app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    return app
