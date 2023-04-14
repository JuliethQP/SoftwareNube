from flask import request, flash,jsonify
from .models import db, UsuarioSchema, Usuario
from flask_restful import Resource
# from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import hashlib

usuario_schema = UsuarioSchema()


class VistaUsuarios(Resource):

    def post(self):
        email_request=request.json["email"]   
        usuario_request = request.json["username"]
        correo_usuario_nuevo = Usuario.query.filter_by(email=email_request).all()
        usuario_nuevo= Usuario.query.filter_by(username=usuario_request).all()
        password1=request.json["password"]
        password2=request.json["password_confirmation"]
        
        try:
            if correo_usuario_nuevo or usuario_nuevo :
                return {'mensaje':'El correo o usuario ya existe'}, 401           
      
            if (password1 != password2):
                return  {'mensaje':'contraseña y confirmación de contraseña son diferentes'}, 401
            
            else:
                password1_encriptada = hashlib.md5(request.json["password"].encode('utf-8')).hexdigest()
                password2_encriptada = hashlib.md5(request.json["password_confirmation"].encode('utf-8')).hexdigest()
                nueva_usuario = Usuario(username=request.json["username"],
                                        email=email_request, 
                                        password1=password1_encriptada,
                                        password2=password2_encriptada
                                        )
                db.session.add(nueva_usuario)
                db.session.commit()
                usuario_schema.dump(nueva_usuario)
                return {'mensaje':'usuario creado exitosamente'}, 201
            
        except db.exc.DataError as e:
            flash('Error: {}'.format(str(e.orig)))
            db.session.rollback()
            
        
class VistaLogin(Resource):
    def post(self):       
        usuario_request = request.json["username"]
        username_input = Usuario.query.filter_by(username=usuario_request).all()  
        contrasena_encriptada = hashlib.md5(
            request.json["password"].encode('utf-8')).hexdigest()
        password_input = Usuario.query.filter_by(password1=contrasena_encriptada).all()   
        try:
            if username_input and password_input:
                payload = {"status":200}
                token = create_access_token(
                identity=1, additional_claims=payload)
                return jsonify(access_token=token)           
            
        except db.exc.DataError as e:
            flash('Error: {}'.format(str(e.orig)))
            db.session.rollback()
            
class VistaTasks(Resource):
    @jwt_required()
    def get(self):        
        try:
            return {'mensaje':'prueba'}, 201                     
                
        except db.exc.DataError as e:
                flash('Error: {}'.format(str(e.orig)))
                db.session.rollback()
            
    