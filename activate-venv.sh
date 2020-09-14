#!/bin/bash
if [ ! -d .venv ]
then
    echo '.venv does not exist--creating...'
    virtualenv .venv
    source .venv/bin/activate
    pip install -e .
    echo "export FLASK_APP=$(pwd)/web" >> .venv/bin/activate
    export FLASK_APP=$(pwd)/web
else
    source .venv/bin/activate
fi