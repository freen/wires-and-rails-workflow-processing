#!/usr/bin/env bash

# Run from /app

python3 main.py

pushd /tmp
    ocropus-nlbin 5823821_0.png
    ocropus-gpageseg -d --maxcolseps 0 --maxseps 0 --hscale 100 5823821_0.png
popd
