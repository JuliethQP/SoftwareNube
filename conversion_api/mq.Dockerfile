FROM python:3.9.16-slim-buster

# Set working directory
WORKDIR /app

RUN ls -lac
# Copy the requirements file
COPY requirements.txt .

# Install dependencies

RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Iniciar el servicio Celery
CMD ["celery", "-A", "mensajeria.task", "worker", "--loglevel=info"]