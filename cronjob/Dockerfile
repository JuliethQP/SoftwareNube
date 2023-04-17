FROM ubuntu:20.04

# Copia el archivo cronjob
COPY cronjob /etc/cron.d/

# Instala cron y otros paquetes
RUN apt-get update && apt-get -y install cron

# Copia los archivos de la aplicación

COPY requirements.txt .

# Instala dependencias
RUN apt-get update && apt-get -y install python3-pip

# Establece el comando de inicio
CMD service cron start
