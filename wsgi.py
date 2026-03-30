import sys
import os

# Set current project path
path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.insert(0, path)

from app import create_app

# PythonAnywhere looks for a variable called 'application'
application = create_app()
