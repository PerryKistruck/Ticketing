from flask import Flask, render_template, session, redirect, url_for
from config import Config
from models import db
from routes import register_routes
from auth.auth_utils import get_current_user, admin_required
import logging
import sys

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging for Azure
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db.init_app(app)

# Register API routes
register_routes(app)

# Create tables with error handling
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        logger.error(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

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
    app.run(debug=True)