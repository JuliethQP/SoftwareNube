from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String, nullable=False)
    email = db.Column(db.String,unique=True, nullable=False)
    password1 = db.Column(db.String, nullable=False)   
    password2 = db.Column(db.String, nullable=False) 
    
class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True