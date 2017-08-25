FROM edoburu/python-runner:latest

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt
RUN bash bin/install-ocropy.sh
