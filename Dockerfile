FROM edoburu/python-runner:latest

RUN apt-get clean && apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'

RUN apt-get -y install cron
RUN touch /var/log/cron.log

WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt
RUN bash bin/install-ocropy.sh

# ADD crontab /etc/cron.d/wires-and-rails-cron
# RUN chmod 0644 /etc/cron.d/wires-and-rails-cron

RUN (crontab -l ; echo "*/5 * * * * /usr/bin/python3 /app/kmeans_and_enqueue_completed_subjects.py >> /var/log/cron.log") | crontab

CMD cron && : >> /var/log/cron.log && tail -f /var/log/cron.log
