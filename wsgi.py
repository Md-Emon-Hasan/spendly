import sys
import os

# Set current project path
path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.insert(0, path)

from app import create_app
from init_db import init_db

# Auto-initialize database on startup 
# (Safe because it uses CREATE TABLE IF NOT EXISTS)
try:
    print("Running database initialization...")
    init_db()
    print("Database initialization complete.")
except Exception as e:
    print(f"Database initialization failed: {e}")

# PythonAnywhere/Render look for a variable called 'application'
application = create_app()
