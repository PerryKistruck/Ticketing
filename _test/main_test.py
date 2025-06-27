"""
Unit tests for the main application module.
"""
import unittest
from models import db
from _test.conftest import create_test_app, create_test_user


class TestMainApp(unittest.TestCase):
    """Test cases for main application routes and functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test users
        self.user = create_test_user()
        self.admin = create_test_user(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_home_route(self):
        """Test the home page route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())
    
    def test_about_route(self):
        """Test the about page route."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())
    
    def test_dashboard_unauthenticated(self):
        """Test dashboard access without authentication."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.location.endswith('/api/auth/login'))
    
    def test_dashboard_authenticated(self):
        """Test dashboard access with authentication."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())
    
    def test_admin_dashboard_unauthenticated(self):
        """Test admin dashboard access without authentication."""
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.location.endswith('/api/auth/login'))
    
    def test_admin_dashboard_non_admin(self):
        """Test admin dashboard access with non-admin user."""
        # Login as regular user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertTrue(response.location.endswith('/'))
    
    def test_admin_dashboard_admin_user(self):
        """Test admin dashboard access with admin user."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())
    
    def test_context_processor_no_user(self):
        """Test context processor when no user is logged in."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # The template should render without errors even with no current_user
    
    def test_context_processor_with_user(self):
        """Test context processor with logged in user."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # The template should render with current_user available
    
    def test_nonexistent_route(self):
        """Test accessing a non-existent route."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_routes_registration(self):
        """Test that all routes are properly registered."""
        # Check that API routes are registered
        with self.app.test_request_context():
            # These should not raise exceptions
            from werkzeug.routing import BuildError
            
            try:
                from flask import url_for
                url_for('auth.login')
                url_for('tickets.get_tickets')
                url_for('users.get_users')
            except BuildError:
                self.fail("Routes are not properly registered")
    
    def test_database_initialization(self):
        """Test that database is properly initialized."""
        # Check that tables exist
        from sqlalchemy import inspect
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        self.assertIn('users', tables)
        self.assertIn('tickets', tables)
    
    def test_app_configuration(self):
        """Test that application is properly configured."""
        self.assertTrue(self.app.config['TESTING'])
        self.assertEqual(self.app.config['SECRET_KEY'], 'test-secret-key')
        self.assertFalse(self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])


class TestAppErrorHandling(unittest.TestCase):
    """Test error handling in the main application."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_invalid_session_handling(self):
        """Test handling of invalid session data."""
        # Set invalid user_id in session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 999  # Non-existent user
        
        # Should not crash, should handle gracefully
        response = self.client.get('/dashboard')
        # Should redirect to login due to invalid session
        self.assertEqual(response.status_code, 302)
    
    def test_malformed_request_handling(self):
        """Test handling of malformed requests."""
        # Send malformed JSON
        response = self.client.post('/api/auth/login', 
                                  data='invalid json',
                                  content_type='application/json')
        # Should handle gracefully, not crash
        self.assertIn(response.status_code, [400, 401])


class TestAppSecurity(unittest.TestCase):
    """Test security aspects of the application."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_session_security(self):
        """Test session security configuration."""
        # App should have a secret key configured
        self.assertIsNotNone(self.app.config.get('SECRET_KEY'))
        self.assertNotEqual(self.app.config.get('SECRET_KEY'), '')
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection."""
        # Create a user
        user = create_test_user()
        
        # Login
        with self.client.session_transaction() as sess:
            sess['user_id'] = user.id
        
        # Try SQL injection in ticket creation
        malicious_data = {
            'title': "'; DROP TABLE tickets; --",
            'description': 'Malicious description'
        }
        
        response = self.client.post('/api/tickets/', json=malicious_data)
        # Should not cause SQL injection, either succeed or fail gracefully
        self.assertIn(response.status_code, [200, 201, 400])
        
        # Check that tickets table still exists
        from models import Ticket
        tickets = Ticket.query.all()
        # This should not fail due to dropped table
        self.assertIsInstance(tickets, list)


if __name__ == '__main__':
    unittest.main()
