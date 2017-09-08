FROM edoburu/python-runner:latest

RUN apt-get clean && apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'

RUN apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Processing app / Python 3
COPY requirements.txt /tmp/pip3-requirements.txt
RUN pip3 install -r /tmp/pip3-requirements.txt

# Ocropy / Python 2
RUN apt-get -y install python-tk
RUN mkdir -p /app && git clone https://github.com/tmbdev/ocropy.git /app/ocropy
COPY en-default.pyrnn.gz /app/ocropy/models/en-default.pyrnn.gz
WORKDIR /app/ocropy
RUN python setup.py install && pip install -r requirements.txt

WORKDIR /app
ADD . /app

ENTRYPOINT ["/usr/bin/supervisord", "-n"]
