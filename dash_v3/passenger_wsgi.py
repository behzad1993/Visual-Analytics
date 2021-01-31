import imp
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import server
application = server

