from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String,unique=True, nullable=False)
    password1 = db.Column(db.String, nullable=False)   
    password2 = db.Column(db.String, nullable=False) 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    file_name = db.Column(db.String, nullable=False)
    origin_format = db.Column(db.String, nullable=False)
    new_format = db.Column(db.String, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String, nullable=False)

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
    id = fields.String()

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        load_instance = True
    id = fields.String()
    status = fields.String()