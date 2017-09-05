FROM edoburu/python-runner:latest

RUN apt-get clean && apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'

WORKDIR /app

ADD . /app

RUN touch /app/log/cron.log

RUN pip3 install -r requirements.txt
RUN bash bin/install-ocropy.sh

RUN apt-get install -y supervisor

COPY supervisord.conf /etc/supervisor/supervisord.conf

ENTRYPOINT ["/usr/bin/supervisord", "-c /app/supervisord.conf", "-n"]
