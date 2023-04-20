from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import apirest.models
from datetime import timedelta
from redis import Redis

def create_app(config_name):
    app = Flask(__name__)  
    
    Redis(host='redis', port=6379, db=0, password='redisultramegasecurepassword')

    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversion_api.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS']=True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    return app

# def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    try:
        app.config.from_pyfile('config.py')
    except:
        pass

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
  
    with app.app_context():
        db.create_all()

    api.init_app(app)

    return app