from apirest import create_app
from apirest.models import db
from apirest.views import VistaUsuarios, VistaLogin, VistaConvertionTask
from flask_restful import Api
from flask_jwt_extended import JWTManager

app=create_app('default')
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

jwt = JWTManager(app)