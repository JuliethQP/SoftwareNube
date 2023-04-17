FROM ubuntu:20.04

WORKDIR /app

# Copia el archivo cronjob
COPY cronjob.sh /root/cronjob.sh

# Give execution rights on the cron scripts
RUN chmod 0644 /root/cronjob.sh

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

#Install Cron
RUN apt-get update
RUN apt-get -y install cron


# Add the cron job
RUN crontab -l | { cat; echo "* * * * * bash /root/cronjob.sh"; } | crontab -

# Run the command on container startup
CMD cron