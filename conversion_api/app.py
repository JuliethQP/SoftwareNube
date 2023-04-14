from apirest import create_app
from apirest.models import db
from apirest.views import VistaUsuarios
from flask_restful import Api

app=create_app('default')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaUsuarios, '/api/auth/signup')