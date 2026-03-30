import os

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(basedir)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-spendly-key'
    DATABASE = os.path.join(project_root, 'database', 'spendly.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
