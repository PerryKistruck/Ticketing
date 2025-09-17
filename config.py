import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration for Azure
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Force HTTPS in production
    is_azure = os.environ.get('WEBSITE_SITE_NAME') is not None
    is_production = os.environ.get('FLASK_ENV') == 'production' or is_azure
    PREFERRED_URL_SCHEME = 'https' if is_production else 'http'
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true' or is_azure

    # Asset versioning removed per user request; relying on default caching behavior.