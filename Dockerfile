FROM edoburu/python-runner:latest

WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt
RUN bash bin/install-ocropy.sh
