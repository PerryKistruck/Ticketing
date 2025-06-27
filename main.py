from flask import Flask, render_template, session, redirect, url_for, jsonify
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

@app.route('/debug/session')
def debug_session():
    """Debug endpoint to check session and user status"""
    try:
        session_data = dict(session)
        current_user = get_current_user()
        
        debug_info = {
            "session_data": session_data,
            "has_user_id": 'user_id' in session,
            "user_id_value": session.get('user_id'),
            "current_user": current_user.to_dict() if current_user else None,
            "secret_key_set": bool(app.config.get('SECRET_KEY')),
            "database_uri": app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50] + "..." if app.config.get('SQLALCHEMY_DATABASE_URI') else 'Not set'
        }
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Debug session error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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