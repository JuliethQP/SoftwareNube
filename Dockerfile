FROM python:3.9.16-slim-buster


# Copiar la aplicación
COPY . /app

# Iniciar el servicio Celery
CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info"]
