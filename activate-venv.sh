#!/bin/bash
if [ ! -d .venv ]
then
    echo '.venv does not exist--creating...'
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    echo 'export FLASK_APP=$VIRTUAL_ENV/../web/voro.py' >> .venv/bin/activate
    export FLASK_APP=$VIRTUAL_ENV/../web/voro.py
else
    source .venv/bin/activate
fi