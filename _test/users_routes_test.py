"""
Unit tests for the users routes module.
"""
import unittest
import json
from models import db, User, Ticket
from _test.conftest import create_test_app, create_test_user, create_test_ticket


class TestUsersRoutes(unittest.TestCase):
    """Test cases for users routes."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test users
        self.user = create_test_user()
        self.other_user = create_test_user(
            username="otheruser",
            email="other@example.com"
        )
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_users_authenticated(self):
        """Test getting all users when authenticated."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # Should return both users
        
        usernames = [user['username'] for user in data]
        self.assertIn('testuser', usernames)
        self.assertIn('otheruser', usernames)
    
    def test_get_users_unauthenticated(self):
        """Test getting users without authentication."""
        response = self.client.get('/api/users/',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
    
    def test_create_user(self):
        """Test creating a new user via API."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/users/', json=user_data)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertEqual(data['username'], 'newuser')
        self.assertEqual(data['email'], 'newuser@example.com')
        self.assertEqual(data['first_name'], 'New')
        self.assertEqual(data['last_name'], 'User')
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('newpass123'))
    
    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username."""
        user_data = {
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'first_name': 'Different',
            'last_name': 'User',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/users/', json=user_data)
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Username or email already exists')
    
    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email."""
        user_data = {
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists
            'first_name': 'Different',
            'last_name': 'User',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/users/', json=user_data)
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Username or email already exists')
    
    def test_get_single_user_self(self):
        """Test getting own user profile."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/users/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], 'testuser')
    
    def test_get_single_user_other(self):
        """Test getting another user's profile (should be denied)."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/users/{self.other_user.id}')
        self.assertEqual(response.status_code, 403)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Access denied')
    
    def test_get_single_user_unauthenticated(self):
        """Test getting user profile without authentication."""
        response = self.client.get(f'/api/users/{self.user.id}',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_user_self(self):
        """Test updating own user profile."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.put(f'/api/users/{self.user.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['first_name'], 'Updated')
        self.assertEqual(data['last_name'], 'Name')
        self.assertEqual(data['email'], 'updated@example.com')
        
        # Verify changes in database
        user = User.query.get(self.user.id)
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')
        self.assertEqual(user.email, 'updated@example.com')
    
    def test_update_user_password(self):
        """Test updating user password."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        update_data = {
            'password': 'newpassword123'
        }
        
        response = self.client.put(f'/api/users/{self.user.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify password was changed
        user = User.query.get(self.user.id)
        self.assertTrue(user.check_password('newpassword123'))
        self.assertFalse(user.check_password('testpass123'))  # Old password
    
    def test_update_user_other(self):
        """Test updating another user's profile (should be denied)."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        update_data = {
            'first_name': 'Unauthorized'
        }
        
        response = self.client.put(f'/api/users/{self.other_user.id}', json=update_data)
        self.assertEqual(response.status_code, 403)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Access denied')
    
    def test_update_user_unauthenticated(self):
        """Test updating user without authentication."""
        update_data = {
            'first_name': 'Unauthorized'
        }
        
        response = self.client.put(f'/api/users/{self.user.id}', json=update_data)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_self(self):
        """Test deleting own user account."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.delete(f'/api/users/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['message'], 'User deleted successfully')
        
        # Verify user was deleted
        user = User.query.get(self.user.id)
        self.assertIsNone(user)
    
    def test_delete_user_other(self):
        """Test deleting another user's account (should be denied)."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.delete(f'/api/users/{self.other_user.id}')
        self.assertEqual(response.status_code, 403)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Access denied')
    
    def test_delete_user_unauthenticated(self):
        """Test deleting user without authentication."""
        response = self.client.delete(f'/api/users/{self.user.id}',
                                    headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
    
    def test_get_user_tickets(self):
        """Test getting tickets for a user."""
        # Create some tickets for the user
        ticket1 = create_test_ticket(
            title="User Ticket 1",
            user_id=self.user.id
        )
        ticket2 = create_test_ticket(
            title="User Ticket 2",
            user_id=self.user.id
        )
        # Create ticket for other user (should not be included)
        other_ticket = create_test_ticket(
            title="Other User Ticket",
            user_id=self.other_user.id
        )
        
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/users/{self.user.id}/tickets')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # Should only return user's tickets
        
        ticket_titles = [ticket['title'] for ticket in data]
        self.assertIn("User Ticket 1", ticket_titles)
        self.assertIn("User Ticket 2", ticket_titles)
        self.assertNotIn("Other User Ticket", ticket_titles)
    
    def test_get_user_tickets_other_user(self):
        """Test getting tickets for another user (should be denied)."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/users/{self.other_user.id}/tickets')
        self.assertEqual(response.status_code, 403)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Access denied')
    
    def test_get_user_tickets_unauthenticated(self):
        """Test getting user tickets without authentication."""
        response = self.client.get(f'/api/users/{self.user.id}/tickets',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)


class TestUsersRoutesEdgeCases(unittest.TestCase):
    """Test edge cases for users routes."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        self.user = create_test_user()
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_nonexistent_user(self):
        """Test getting a non-existent user."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/users/999')
        self.assertEqual(response.status_code, 403)  # Access denied before 404
    
    def test_update_nonexistent_user(self):
        """Test updating a non-existent user."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.put('/api/users/999', json={'first_name': 'Updated'})
        self.assertEqual(response.status_code, 403)  # Access denied before 404
    
    def test_delete_nonexistent_user(self):
        """Test deleting a non-existent user."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.delete('/api/users/999')
        self.assertEqual(response.status_code, 403)  # Access denied before 404
    
    def test_create_user_missing_required_fields(self):
        """Test creating user with missing required fields."""
        user_data = {
            'username': 'newuser'
            # Missing other required fields
        }
        
        response = self.client.post('/api/users/', json=user_data)
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_without_password(self):
        """Test creating user without password."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User'
            # No password field
        }
        
        response = self.client.post('/api/users/', json=user_data)
        # The current implementation expects password and will fail without it
        self.assertEqual(response.status_code, 400)  # Should fail validation
    
    def test_update_user_partial_data(self):
        """Test updating user with partial data."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        # Only update first name
        update_data = {
            'first_name': 'PartialUpdate'
        }
        
        response = self.client.put(f'/api/users/{self.user.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['first_name'], 'PartialUpdate')
        self.assertEqual(data['last_name'], 'User')  # Should remain unchanged
        self.assertEqual(data['username'], 'testuser')  # Should remain unchanged


if __name__ == '__main__':
    unittest.main()
