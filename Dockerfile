FROM edoburu/python-runner:latest

RUN apt-get clean && apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'

RUN apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Processing app / Python 3
COPY requirements.txt /tmp/pip3-requirements.txt
RUN pip3 install -r /tmp/pip3-requirements.txt

# Ocropy / Python 2
RUN mkdir -p /app && apt-get -y install wget python-tk && git clone https://github.com/tmbdev/ocropy.git /app/ocropy
COPY en-default.pyrnn.gz /tmp/en-default.pyrnn.gz
COPY bin/install-ocropy.sh /tmp/install-ocropy.sh
RUN bash /tmp/install-ocropy.sh

# RUN touch /app/log/cron.log

ADD . /app

ENTRYPOINT ["/usr/bin/supervisord", "-n"]
