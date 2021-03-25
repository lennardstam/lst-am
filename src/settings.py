import os


SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3' #os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# SERVER_NAME = '127.0.0.1'
SECRET_KEY = os.environ.get('SECRET_KEY') or 'ronisgek'
