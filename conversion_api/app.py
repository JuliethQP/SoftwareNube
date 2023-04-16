from apirest import create_app
from apirest.models import *
from apirest.views import *
from flask_restful import Api
from flask_jwt_extended import JWTManager

app=create_app('tasks')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)

#Gestión de usuarios
api.add_resource(VistaUsuarios, '/api/auth/signup')
api.add_resource(VistaLogin, '/api/auth/login')

#Tareas de conversion
api.add_resource(VistaConvertionTask, '/api/tasks')
api.add_resource(VistaTask, '/api/task/<int:id_task>')
api.add_resource(VistaFile, '/api/files/<string:filename>/<int:type>')

#Convertir los archivos pendientes
api.add_resource(VistaProcesarArchivos, '/api/process')

jwt = JWTManager(app)