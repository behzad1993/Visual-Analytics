#!/bin/bash

# open webserver directory
cd dash_v2

# install all dependencies
pip install -r requirements.txt

# run webserver
python app.py
