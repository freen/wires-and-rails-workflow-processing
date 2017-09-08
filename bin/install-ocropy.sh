#!/usr/bin/env bash

apt-get -y install wget python-tk

git clone https://github.com/tmbdev/ocropy.git
pushd ocropy
    mv /app/en-default.pyrnn.gz models/
    python setup.py install
    pip install -r requirements.txt
popd
