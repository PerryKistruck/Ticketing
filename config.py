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

    # Asset versioning: prefer explicit env (ASSET_VERSION or APP_VERSION). If absent, derive a stable
    # value per deployment from a combination of deployment date and latest static file mtime.
    # This avoids changing on every process restart but updates when static assets change.
    _explicit_version = os.environ.get('ASSET_VERSION') or os.environ.get('APP_VERSION')
    if _explicit_version:
        ASSET_VERSION = _explicit_version
    else:
        try:
            static_root = os.path.join(os.path.dirname(__file__), 'static')
            latest_mtime = 0
            for root, dirs, files in os.walk(static_root):
                for f in files:
                    full = os.path.join(root, f)
                    try:
                        m = os.path.getmtime(full)
                        if m > latest_mtime:
                            latest_mtime = m
                    except OSError:
                        pass
            from datetime import datetime
            date_part = datetime.utcnow().strftime('%Y%m%d')
            # Round mtime to an integer to keep it short
            mtime_part = str(int(latest_mtime))[-6:] if latest_mtime else '000000'
            ASSET_VERSION = f"{date_part}.{mtime_part}"
        except Exception:
            # Fallback stable default
            ASSET_VERSION = 'v1'