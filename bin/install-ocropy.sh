#!/usr/bin/env bash

pushd /app/ocropy
    mv /tmp/en-default.pyrnn.gz models/
    python setup.py install
    pip install -r requirements.txt
popd
