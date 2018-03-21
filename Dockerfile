FROM edoburu/python-runner:latest

RUN apt-get clean && apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'

# Processing app / Python 3
COPY requirements.txt /tmp/pip3-requirements.txt
RUN pip3 install -r /tmp/pip3-requirements.txt

# Ocropy / Python 2
RUN apt-get update && apt-get -y install wget python-tk
# RUN mkdir -p /app && git clone https://github.com/tmbdev/ocropy.git /app/ocropy
RUN mkdir -p /app && git clone -b fix-typeerror-numpy https://github.com/zuphilip/ocropy.git /app/ocropy
RUN wget -nd http://www.tmbdev.net/en-default.pyrnn.gz && mv en-default.pyrnn.gz /app/ocropy/models/en-default.pyrnn.gz
WORKDIR /app/ocropy
RUN python setup.py install && pip install -r requirements.txt

# supervisord
RUN apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf

WORKDIR /app
ADD . /app

ENTRYPOINT ["/usr/bin/supervisord", "-n"]
