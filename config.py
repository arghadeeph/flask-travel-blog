from dotenv import load_dotenv
import os
from datetime import timedelta


load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = True
    # Configuration for mail server (example using Gmail SMTP)
    MAIL_USERNAME = 'arghadeeph@gmail.com'
    MAIL_PASSWORD = 'ksmiedstiagpvkrw'
    MAIL_DEFAULT_SENDER = 'arghadeeph@gmail.com'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    FILE_UPLOAD_PATH = 'static/uploads/'