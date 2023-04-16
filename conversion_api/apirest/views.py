from flask import request, flash,jsonify
from .models import db, UsuarioSchema, Usuario, Task, TaskSchema
from mensajeria import process_files, registrar_log

from flask_restful import Resource
# from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename

import os

import hashlib

usuario_schema = UsuarioSchema()
task_schema = TaskSchema()

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
                token = create_access_token(identity=1, additional_claims=payload)        
                registrar_log(usuario_request, datetime.now())     
                return jsonify(access_token=token)           
            
        except db.exc.DataError as e:
            flash('Error: {}'.format(str(e.orig)))
            db.session.rollback()

class VistaConvertionTask(Resource):
    #Enpoint para la creación de una tarea de conversión
    def post(self):
        valid_formats = ['zip', '7z', 'tar.gz', 'tarbz2']

        uploaded_file = request.files.get('fileName')
        file_name =  secure_filename(datetime.now().strftime("%m%d%Y%H%M%S") + '--' + uploaded_file.filename)

        origin_format = uploaded_file.mimetype.split('/')[1]
        new_format = request.form.getlist('newFormat')[0]

        if origin_format == new_format:
            return {'mensaje':'El formato origen y destino son el mismo, no se realizará ningun proceso de conversión dado el escenario expuesto.'}, 200
        elif new_format in valid_formats:
            file_path = os.getcwd() + '/files/' + file_name
            uploaded_file.save(file_path)

            nueva_conversion = Task(file_name=file_name, origin_format=origin_format, new_format=new_format, status=0, timestamp=datetime.now())
            
            db.session.add(nueva_conversion)
            db.session.commit()
            usuario_schema.dump(nueva_conversion)

            return task_schema.dump(nueva_conversion), 202
        else:
            return {'mensaje':'Lo sentimos nuestro sistema no soporta dicho formato de conversión'}, 400

class VistaProcesarArchivos(Resource):
    #Funcion para procesar los archivos
    def get(self):
        file_for_process = Task.query.filter_by(status=0)

        for file in file_for_process:
            process_files.delay(task_schema.dump(file))

        return str(file_for_process.count()) + ' files be process'