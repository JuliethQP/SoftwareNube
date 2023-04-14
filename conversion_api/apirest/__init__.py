from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import apirest.models
# import models

# import flask.scaffold
# flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func

# from flask_restful import Api
# from flask_jwt_extended import JWTManager

# db = SQLAlchemy()
# ma = Marshmallokw()
# jwt = JWTManager()
# api = Api()


def create_app(config_name):
    app = Flask(__name__)  
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversion_api.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

# def _endpoint_from_view_func(view_func):
#     """Internal helper that returns the default endpoint for a given
#     function.  This always is the function name.
#     """
#     assert view_func is not None, "expected view func if endpoint is not provided."
#     return view_func.__name__