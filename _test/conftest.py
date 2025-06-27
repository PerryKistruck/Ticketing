"""
Test configuration and utilities for the ticketing system.
"""
import os
import tempfile
from flask import Flask
from models import db, User, Ticket


class TestConfig:
    """Test configuration class."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


def create_test_app():
    """Create and configure a test Flask application."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Initialize database
    db.init_app(app)
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    # Add main app routes for testing
    from auth.auth_utils import get_current_user, admin_required
    
    @app.context_processor
    def inject_user():
        return dict(current_user=get_current_user())
    
    @app.route('/')
    def home():
        return '<html><body>Home</body></html>'
    
    @app.route('/about')
    def about():
        return '<html><body>About</body></html>'
    
    @app.route('/dashboard')
    def dashboard():
        user = get_current_user()
        if not user:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return '<html><body>Dashboard</body></html>'
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        user = get_current_user()
        return '<html><body>Admin Dashboard</body></html>'
    
    return app


def create_test_user(username="testuser", email="test@example.com", 
                    first_name="Test", last_name="User", 
                    password="testpass123", is_admin=False):
    """Create a test user."""
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_admin=is_admin
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def create_test_ticket(title="Test Ticket", description="Test Description",
                      user_id=1, status="open", priority="medium", 
                      assigned_to=None):
    """Create a test ticket."""
    ticket = Ticket(
        title=title,
        description=description,
        user_id=user_id,
        status=status,
        priority=priority,
        assigned_to=assigned_to
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket


def login_user(client, username="testuser", password="testpass123"):
    """Helper function to log in a user during tests."""
    return client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })


def logout_user(client):
    """Helper function to log out a user during tests."""
    return client.post('/api/auth/logout', 
                      headers={'Content-Type': 'application/json'})
