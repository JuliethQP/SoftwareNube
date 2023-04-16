from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import apirest.models

def create_app(config_name):
    app = Flask(__name__)  
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversion_api.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS']=True
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