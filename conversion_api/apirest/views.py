from flask import request, flash
from .models import db, UsuarioSchema, Usuario
from flask_restful import Resource
# from sqlalchemy.exc import IntegrityError


usuario_schema = UsuarioSchema()


class VistaUsuarios(Resource):

    def post(self):
        email_request=request.json["email"]   
        usuario_request=  user=request.json["user"]
        correo_usuario_nuevo = Usuario.query.filter_by(email=email_request).all()
        usuario_nuevo= Usuario.query.filter_by(user=usuario_request).all()
        password1=request.json["password"]
        password2=request.json["password_confirmation"]
        
        try:
            if correo_usuario_nuevo or usuario_nuevo :
                return {'mensaje':'El correo o usuario ya existe'}, 401           
      
            if (password1 != password2):
                return  {'mensaje':'contraseña y confirmación de contraseña son diferentes'}, 401
            
            else:
                nueva_usuario = Usuario(user=request.json["user"], email=email_request, password1=request.json["password"],password2=request.json["password_confirmation"])
                db.session.add(nueva_usuario)
                db.session.commit()
                usuario_schema.dump(nueva_usuario)
                return {'mensaje':'usuario creado exitosamente'}, 201
            
        except db.exc.DataError as e:
            flash('Error: {}'.format(str(e.orig)))
            db.session.rollback()
            
        

    