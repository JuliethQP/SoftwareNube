FROM python:3.9.16-slim-buster

ENV PYTHONUNBUFFERED True
# Set working directory
WORKDIR /app

RUN mkdir /app/files
# Copy the requirements file
COPY requirements.txt .

# Install dependencies

RUN pip3 install -r requirements.txt


# Copy the rest of the application code
COPY . .

EXPOSE 8080
#EXPOSE 8080

ENV FLASK_APP=flaskr/app.py
# Start the application
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8080"]
#CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 app:app