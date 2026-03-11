import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'foodbridge-secret-key-12345'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '1234'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'foodbridge'
    MYSQL_PORT = 3306
    MYSQL_UNIX_SOCKET = None
    MYSQL_CONNECT_TIMEOUT = 10
    MYSQL_READ_DEFAULT_FILE = None
    MYSQL_USE_UNICODE = True
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_SQL_MODE = None
    MYSQL_CURSORCLASS = 'DictCursor'
    MYSQL_AUTOCOMMIT = True
    MYSQL_USE_SSL = None
    MYSQL_CUSTOM_OPTIONS = None
    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_KEY = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY') or 'firebase-adminsdk.json'
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyDjSmsXw1QHCeOHGAQJvA62ZQOkZxHx2pY",
        "authDomain": "my-app-f9d15.firebaseapp.com",
        "projectId": "my-app-f9d15",
        "storageBucket": "my-app-f9d15.firebasestorage.app",
        "messagingSenderId": "643375851931",
        "appId": "1:643375851931:web:79bd6f69e0eb7c5a56993e",
        "measurementId": "G-K5ML7GX6QV"
    }
