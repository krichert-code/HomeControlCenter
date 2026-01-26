#!/bin/bash

if [ -f /var/run/hcc.lock ]; then
    exit 0
fi
touch /var/run/hcc.lock

source ~/py_envs/bin/activate
python3 ./hcc.py

exit 0

