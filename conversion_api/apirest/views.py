from flask import request, flash, jsonify, send_file
from .models import db, UsuarioSchema, Usuario, Task, TaskSchema
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import hashlib
from google.cloud import storage, pubsub_v1
import uuid
import json

client = storage.Client()
bucket = client.bucket('bucket-flask-app')

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("proyecto-software-en-la-nube", "topic-proyecto-conversor-sub")
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("proyecto-software-en-la-nube", "suscripcion-proyecto-conversor-001")

usuario_schema = UsuarioSchema()
task_schema = TaskSchema()


class VistaUsuarios(Resource):
    def post(self):
        email_request = request.json["email"]
        usuario_request = request.json["username"]
        correo_usuario_nuevo = Usuario.query.filter_by(
            email=email_request).all()
        usuario_nuevo = Usuario.query.filter_by(username=usuario_request).all()
        password1 = request.json["password"]
        password2 = request.json["password_confirmation"]

        try:
            if correo_usuario_nuevo or usuario_nuevo:
                return {'mensaje': 'El correo o usuario ya existe'}, 401

            if (password1 != password2):
                return {'mensaje': 'contraseña y confirmación de contraseña son diferentes'}, 401

            else:
                password1_encriptada = hashlib.md5(
                    request.json["password"].encode('utf-8')).hexdigest()
                password2_encriptada = hashlib.md5(
                    request.json["password_confirmation"].encode('utf-8')).hexdigest()
                nueva_usuario = Usuario(username=request.json["username"],
                                        email=email_request,
                                        password1=password1_encriptada,
                                        password2=password2_encriptada
                                        )
                db.session.add(nueva_usuario)
                db.session.commit()
                usuario_schema.dump(nueva_usuario)
                return {'mensaje': 'usuario creado exitosamente'}, 201

        except db.exc.DataError as e:
            flash('Error: {}'.format(str(e.orig)))
            db.session.rollback()


class VistaLogin(Resource):
    def post(self):
        usuario_request = request.json["username"]
        username_input = Usuario.query.filter_by(
            username=usuario_request).all()
        contrasena_encriptada = hashlib.md5(
            request.json["password"].encode('utf-8')).hexdigest()
        password_input = Usuario.query.filter_by(
            password1=contrasena_encriptada).all()
        try:
            if username_input and password_input:
                payload = {"status": 200}
                token = create_access_token(
                    identity=1, additional_claims=payload)
                return jsonify(access_token=token)
            else:
                return {"mensaje": "usuario no existe"}

        except db.exc.DataError as e:
            flash('Error: {}'.format(str(e.orig)))
            db.session.rollback()


class VistaConvertionTask(Resource):
    @jwt_required()
    def get(self):
        tasks = Task.query.all()
        return [task_schema.dump(task) for task in tasks]

    # Enpoint para la creación de una tarea de conversión
    @jwt_required()
    def post(self):
        valid_formats = ['zip', 'tar.gz', 'tar.bz2',
                         'gz', 'bz2', 'tarbz2', 'targz']

        uploaded_file = request.files.get('fileName')
        idUnico = str(uuid.uuid4())
        file_name = secure_filename(
            idUnico + '--'+datetime.now().strftime("%m%d%Y%H%M%S") + '--' + uploaded_file.filename)

        origin_format = uploaded_file.mimetype.split('/')[1]
        new_format = request.form.getlist('newFormat')[0]

        if origin_format == new_format:
            return {'mensaje': 'El formato origen y destino son el mismo, no se realizará ningun proceso de conversión dado el escenario expuesto.'}, 200
        elif new_format in valid_formats:

            blob = bucket.blob(file_name)
            blob.content_type = uploaded_file.mimetype
            blob.upload_from_file(uploaded_file)

            if new_format == 'tar.gz' or new_format == 'targz':
                new_format = 'gz'

            if new_format == 'tar.bz2' or new_format == 'tarbz2':
                new_format = 'bz2'

            nueva_conversion = Task(file_name=file_name, origin_format=origin_format,
                                    new_format=new_format, status=0, timestamp=datetime.now())
            # eliminar el archivo en la maquina virtual cuando se sube
            # crear acá la conexion con pub sub , crear la tarea en el pub sub --> guardar el nombre del archivo (file_name) y el formato al que quiere cambiar  y guardarlo en la cola
            db.session.add(nueva_conversion)
            db.session.commit()
            usuario_schema.dump(nueva_conversion)
          
            data = {
                    "filename": file_name,
                    "status": 0,
                    "new_format": new_format
                }
            json_string = json.dumps(data)
            message = json_string
            data = message.encode('utf-8')            
            
           
            future = publisher.publish(topic_path, data)
            print(future.result())    

            return task_schema.dump(nueva_conversion), 202
        else:
            return {'mensaje': 'Lo sentimos nuestro sistema no soporta dicho formato de conversión'}, 400
        

class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        task = Task.query.get_or_404(id_task)
        if task is None:
            return "La tarea con el id dado no existe.", 404
        else:
            return task_schema.dump(task), 200

    # Endpoint con las operaciones relacionadas a una tarea en específico
    @jwt_required()
    def delete(self, id_task):

        try:
            task = Task.query.get_or_404(id_task)

            if task.status != 1:
                return "La tarea con el id dado no se encuentra finalizada, no procede la eliminación.", 400
         
            blob = bucket.blob(task.file_name)            
            blob.delete()
            blob = bucket.blob(task.file_name + '.' + task.new_format)
            blob.delete()       
               
            db.session.delete(task)
            db.session.commit()
            return "Los archivos han sido borrados exitosamente.", 204

        except Exception as ex:
            return str(ex), 500

    @jwt_required()
    def get(self, id_task):
        task = Task.query.get_or_404(id_task)
        if task is None:
            return "La tarea con el id dado no existe.", 404
        else:
            return task_schema.dump(task), 200


class VistaFile(Resource):
    # Endpoint para la consulta de archivos originales (0) y procesados (1)
    # @jwt_required()
    def get(self, filename, type):
        try:
            if type != 0 and type != 1:
                return "Opción errónea de tipo de archivo a obtener (Original --> 0 - Procesado --> 1).", 404

            task = Task.query.filter(Task.file_name == filename).first()           
            files_path_folder = '/tmp'
            if task is None:
                return "No se encuentra la tarea asociada al nombre dado.", 404
            else:
                if type == 0:

                    blob = bucket.blob(filename)
                    if blob is None:
                        return "El archivo no existe en el bucket", 404

                    blob.download_to_filename(
                        f'{files_path_folder}/{filename}')
                    tipo = blob.content_type

                    return send_file(f'{files_path_folder}/{filename}', as_attachment=True, mimetype=tipo)

                else:
                    filedownload = f'{files_path_folder}/{filename}' + \
                        '.' + task.new_format
                    blob = bucket.blob(f'{filename}' + '.' + task.new_format)
                    blob.download_to_filename(filedownload)
                    tipo = blob.content_type
                    return send_file(filedownload, as_attachment=True, mimetype=tipo)   

        except Exception as ex:
            print(ex)
            return str(ex), 500
        
        finally:
            if type == 0:
                ruta = files_path_folder
                archivo = filename
                ruta_archivo = os.path.join(ruta, archivo)
                os.remove(ruta_archivo)
            else:
                try:
                    ruta = files_path_folder
                    ruta_archivo = os.path.join(ruta, filedownload)
                    os.remove(ruta_archivo)
                except Exception as ex:
                     return str(ex), 500