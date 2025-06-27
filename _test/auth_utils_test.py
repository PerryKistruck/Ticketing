"""
Unit tests for the auth utilities module.
"""
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session, request, jsonify
from werkzeug.test import Client
from werkzeug.wrappers import Response
from models import db, User
from auth.auth_utils import login_required, admin_required, get_current_user
from _test.conftest import create_test_app, create_test_user


class TestAuthUtils(unittest.TestCase):
    """Test cases for auth utilities."""
    
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
    
    def test_get_current_user_no_session(self):
        """Test get_current_user when no user is logged in."""
        with self.app.test_request_context():
            user = get_current_user()
            self.assertIsNone(user)
    
    def test_get_current_user_with_session(self):
        """Test get_current_user when user is logged in."""
        # Use Flask's test request context with session
        with self.app.test_request_context() as ctx:
            from flask import session
            session['user_id'] = self.user.id
            
            user = get_current_user()
            self.assertIsNotNone(user)
            self.assertEqual(user.id, self.user.id)
            self.assertEqual(user.username, self.user.username)
    
    def test_get_current_user_invalid_session(self):
        """Test get_current_user with invalid user_id in session."""
        with self.app.test_request_context() as ctx:
            from flask import session
            session['user_id'] = 999  # Non-existent user ID
            
            user = get_current_user()
            self.assertIsNone(user)
    
    def test_login_required_decorator_no_auth(self):
        """Test login_required decorator without authentication."""
        @self.app.route('/test-endpoint')
        @login_required
        def test_endpoint():
            return jsonify({'message': 'success'})
        
        # Test JSON request
        response = self.client.get('/test-endpoint', 
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['error'], 'Authentication required')
    
    def test_login_required_decorator_with_auth(self):
        """Test login_required decorator with authentication."""
        @self.app.route('/test-endpoint')
        @login_required
        def test_endpoint():
            return jsonify({'message': 'success'})
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/test-endpoint')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'success')
    
    def test_admin_required_decorator_no_auth(self):
        """Test admin_required decorator without authentication."""
        @self.app.route('/admin-endpoint')
        @admin_required
        def admin_endpoint():
            return jsonify({'message': 'admin success'})
        
        response = self.client.get('/admin-endpoint',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['error'], 'Authentication required')
    
    def test_admin_required_decorator_non_admin(self):
        """Test admin_required decorator with non-admin user."""
        @self.app.route('/admin-endpoint')
        @admin_required
        def admin_endpoint():
            return jsonify({'message': 'admin success'})
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id  # Regular user, not admin
        
        response = self.client.get('/admin-endpoint',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['error'], 'Admin privileges required')
    
    def test_admin_required_decorator_with_admin(self):
        """Test admin_required decorator with admin user."""
        @self.app.route('/admin-endpoint')
        @admin_required
        def admin_endpoint():
            return jsonify({'message': 'admin success'})
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.get('/admin-endpoint')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'admin success')
    
    def test_login_required_form_request_redirect(self):
        """Test login_required decorator with form request (should redirect)."""
        @self.app.route('/test-form-endpoint')
        @login_required
        def test_form_endpoint():
            return 'success'
        
        response = self.client.get('/test-form-endpoint')
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.location.endswith('/api/auth/login'))
    
    def test_admin_required_form_request_redirect(self):
        """Test admin_required decorator with form request from non-admin."""
        @self.app.route('/admin-form-endpoint')
        @admin_required
        def admin_form_endpoint():
            return 'admin success'
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id  # Regular user
        
        response = self.client.get('/admin-form-endpoint')
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.location.endswith('/'))


class TestAuthDecoratorsIntegration(unittest.TestCase):
    """Integration tests for auth decorators with actual routes."""
    
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
    
    def test_protected_route_access(self):
        """Test accessing protected routes."""
        # Test unauthenticated access - should get redirect for form requests
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test authenticated access
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_route_access(self):
        """Test accessing admin-only routes."""
        # Test unauthenticated access - should get redirect for form requests
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 302)  # Redirect to home
        
        # Test admin access
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
