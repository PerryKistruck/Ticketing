from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from config import Config
from models import db
from routes import register_routes
from auth.auth_utils import get_current_user, admin_required
import logging
import sys
import os

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging for Azure
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force HTTPS in production
is_production = (app.config.get('FLASK_ENV') == 'production' or 
                os.environ.get('WEBSITE_SITE_NAME') or  # Azure App Service
                app.config.get('FORCE_HTTPS'))

if is_production:
    @app.before_request
    def force_https():
        # Handle Azure App Service forwarded headers
        if (not request.is_secure and 
            request.headers.get('X-Forwarded-Proto', '').lower() != 'https' and
            not request.headers.get('X-Azure-Ref')):  # Don't redirect Azure health checks
            if request.method == 'GET':
                return redirect(request.url.replace('http://', 'https://'), code=301)
        
        # Set the URL scheme for url_for to use HTTPS
        if request.headers.get('X-Forwarded-Proto') == 'https':
            request.environ['wsgi.url_scheme'] = 'https'

# Initialize database
db.init_app(app)

# Register API routes
register_routes(app)

# Create tables with error handling
with app.app_context():
    try:
        # Test database connection first
        logger.info(f"Testing database connection...")
        logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        
        # Simple connection test
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        
        # Create tables
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        # Don't fail the app startup - let it run without DB for debugging
        logger.error("App will continue without database connection")

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

@app.after_request
def add_security_headers(response):
    # Add HSTS only when using HTTPS / production conditions
    if is_production:
        response.headers.setdefault('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
    return response

@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}, 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', user=user)

@app.route('/admin')
@admin_required
def admin_dashboard():
    user = get_current_user()
    return render_template('admin_dashboard.html', user=user)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)