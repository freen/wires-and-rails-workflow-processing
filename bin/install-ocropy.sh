#!/usr/bin/env bash

apt-get -y install wget python-tk

git clone https://github.com/tmbdev/ocropy.git
pushd ocropy
    wget -nd http://www.tmbdev.net/en-default.pyrnn.gz
    mv en-default.pyrnn.gz models/
    python setup.py install
    pip install -r requirements.txt
popd
