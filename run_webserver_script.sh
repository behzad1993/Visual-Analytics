#!/bin/bash

# open webserver directory
cd dash_final

# install all dependencies
pip install -r requirements.txt

# run webserver
python app.py
