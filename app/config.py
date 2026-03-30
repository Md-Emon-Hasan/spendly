import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(basedir)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-spendly-key'
    
    # Render provides DATABASE_URL for Postgres
    # If not present, fallback to local SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        # Fix for some SQLAlchemy/Driver versions that prefer 'postgresql://'
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    DATABASE_URI = database_url
    DATABASE_SQLITE = os.path.join(project_root, 'database', 'spendly.db')
    
    # Helper to check if we are in production/Postgres mode
    IS_POSTGRES = DATABASE_URI is not None
