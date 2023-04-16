## Correr la aplicación de flask 
```
cd conversion_api
py -m venv venv
venv\Scripts\activate
pip freeze > requirements.txt
flask run
```

## Correr docker compose
En la raíz del proyecto
```
cd redis
docker compose up redis
```

## Bajar docker compose
En la raíz del proyecto

```
docker compose down
```
## Levantar la cola de mensajeria
En la raíz del proyecto en otra consola 
```
celery -A conversion_api.mensajeria.task worker -l info
```
