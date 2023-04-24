## PARA EJECUTAR LA APP EN DOCKER
En la raíz del proyecto
```
docker-compose up -d
```

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
## Levantar celery en google cloud 
En la raíz del proyecto en otra consola 
```
sudo su
cd SoftwareNube/conversion_api
source lab-celery/bin/activate
celery -A mensajeria.task worker -l info
```
## Levantar redis en google cloud 
```
sudo su
cd SoftwareNube/redis
redis-server ./redis.conf 
```
## Levantar la aplicación de flask en google 
```
sudo su
cd SoftwareNube/conversion_api
source venv/bin/activate 
flask run --port 80 --host 0.0.0.0 
```
