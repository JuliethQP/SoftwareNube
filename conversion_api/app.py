from apirest import create_app
from apirest.models import db
from apirest.views import VistaUsuarios, VistaLogin, VistaTasks
from flask_restful import Api
from flask_jwt_extended import JWTManager

app=create_app('default')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaUsuarios, '/api/auth/signup')
api.add_resource(VistaLogin, '/api/auth/login')
api.add_resource(VistaTasks, '/api/tasks')

jwt = JWTManager(app)