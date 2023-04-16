from flask import request, flash, jsonify, send_from_directory
from .models import db, UsuarioSchema, Usuario, Task, TaskSchema
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
                token = create_access_token(
                identity=1, additional_claims=payload)               
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
        elif origin_format in valid_formats and new_format in valid_formats:
            file_path = os.getcwd() + '/files/' + file_name
            uploaded_file.save(file_path)

            nueva_conversion = Task(file_name=file_name, origin_format=origin_format, new_format=new_format, status=0, timestamp=datetime.now())
            
            db.session.add(nueva_conversion)
            db.session.commit()
            usuario_schema.dump(nueva_conversion)

            return task_schema.dump(nueva_conversion), 202
        else:
            return {'mensaje':'Lo sentimos nuestro sistema no soporta dicho formato de conversión'}, 400
        
    def get(self):
        tasks = Task.query.all()
        return [task_schema.dump(task) for task in tasks]
        
class VistaTask(Resource):
    #Endpoint con las operaciones relacionadas a una tarea en específico
    def delete(self, id_task):

        try:
            task = Task.query.get_or_404(id_task)

            print("llegó")
            if task is None:
                return "La tarea con el id dado no existe.", 404    
            elif task.id != 1:
                return "La tarea con el id dado no se encuentra finalizada, no procede la eliminación.", 400
            
            file_path_origin = os.getcwd() + '/files/' + task.file_name
            file_path_processed = os.getcwd() + '/files/' + task.file_name + '.' + task.new_format

            if os.path.exists(file_path_origin) and os.path.exists(file_path_processed):
                os.remove(file_path_origin)
                os.remove(file_path_processed)
                return "Los archivos han sido borrados exitosamente.", 204
            else:
                return "No se encuentran los archivos a borrar.", 404
        except Exception as ex:
            return str(ex), 500
        
    def get(self, id_task):
        task = Task.query.get_or_404(id_task)
        if task is None:
            return "La tarea con el id dado no existe.", 404
        else: 
            return task_schema.dump(task), 200
        
class VistaFile(Resource):
    #Endpint para la consulta de archivos originales (0) y procesados (1)
    def get(self, filename, type):

        try:
            if type != 0 and type != 1:
                return "Opción errónea de tipo de archivo a obtener (Original --> 0 - Procesado --> 1).", 404

            task = Task.query.filter(Task.file_name == filename).first()
            
            if task is None:
                return "No se encuentra la tarea asociada al nombre dado.", 404
            else:
                files_path_folder = os.getcwd() + '/files/'
                
                if type == 0:
                    return send_from_directory(files_path_folder, task.file_name), 200
                else:
                    return send_from_directory(files_path_folder, task.file_name + '.' + task.new_format), 200

        except Exception as ex:
            return str(ex), 500