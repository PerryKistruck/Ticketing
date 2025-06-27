"""
Unit tests for the tickets routes module.
"""
import unittest
import json
from models import db, User, Ticket
from _test.conftest import create_test_app, create_test_user, create_test_ticket, login_user


class TestTicketsRoutes(unittest.TestCase):
    """Test cases for tickets routes."""
    
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
        self.other_user = create_test_user(
            username="otheruser",
            email="other@example.com"
        )
        
        # Create test tickets
        self.user_ticket = create_test_ticket(
            title="User Ticket",
            description="Ticket created by user",
            user_id=self.user.id
        )
        self.other_user_ticket = create_test_ticket(
            title="Other User Ticket",
            description="Ticket created by other user",
            user_id=self.other_user.id
        )
        self.assigned_ticket = create_test_ticket(
            title="Assigned Ticket",
            description="Ticket assigned to user",
            user_id=self.other_user.id,
            assigned_to=self.user.id
        )
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_tickets_unauthenticated(self):
        """Test getting tickets without authentication."""
        response = self.client.get('/api/tickets/',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
    
    def test_get_tickets_authenticated(self):
        """Test getting tickets when authenticated."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        
        # Should return tickets created by user OR assigned to user
        ticket_titles = [ticket['title'] for ticket in data]
        self.assertIn("User Ticket", ticket_titles)  # Created by user
        self.assertIn("Assigned Ticket", ticket_titles)  # Assigned to user
        self.assertNotIn("Other User Ticket", ticket_titles)  # Not related to user
    
    def test_get_all_tickets_admin(self):
        """Test admin endpoint to get all tickets."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)  # Should return all tickets
    
    def test_get_all_tickets_non_admin(self):
        """Test admin endpoint access by non-admin user."""
        # Login as regular user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/tickets/admin/all',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 403)
    
    def test_get_all_tickets_with_filters(self):
        """Test admin endpoint with filtering."""
        # Create tickets with different statuses and priorities
        create_test_ticket(
            title="Closed Ticket",
            user_id=self.user.id,
            status="closed",
            priority="low"
        )
        
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        # Test status filter
        response = self.client.get('/api/tickets/admin/all?status=open')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        for ticket in data:
            self.assertEqual(ticket['status'], 'open')
        
        # Test priority filter
        response = self.client.get('/api/tickets/admin/all?priority=medium')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        for ticket in data:
            self.assertEqual(ticket['priority'], 'medium')
    
    def test_create_ticket_authenticated(self):
        """Test creating a new ticket when authenticated."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        ticket_data = {
            'title': 'New Test Ticket',
            'description': 'This is a new test ticket',
            'priority': 'high'
        }
        
        response = self.client.post('/api/tickets/', json=ticket_data)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertEqual(data['title'], 'New Test Ticket')
        self.assertEqual(data['description'], 'This is a new test ticket')
        self.assertEqual(data['priority'], 'high')
        self.assertEqual(data['status'], 'open')  # Default status
        self.assertEqual(data['user_id'], self.user.id)
        
        # Verify ticket was created in database
        ticket = Ticket.query.filter_by(title='New Test Ticket').first()
        self.assertIsNotNone(ticket)
    
    def test_create_ticket_unauthenticated(self):
        """Test creating a ticket without authentication."""
        ticket_data = {
            'title': 'New Test Ticket',
            'description': 'This is a new test ticket'
        }
        
        response = self.client.post('/api/tickets/', json=ticket_data)
        self.assertEqual(response.status_code, 401)
    
    def test_create_ticket_missing_title(self):
        """Test creating a ticket without required title."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        ticket_data = {
            'description': 'This is a new test ticket'
            # Missing title
        }
        
        response = self.client.post('/api/tickets/', json=ticket_data)
        self.assertEqual(response.status_code, 400)
    
    def test_get_single_ticket_owner(self):
        """Test getting a single ticket as the owner."""
        # Login as ticket owner
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/tickets/{self.user_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['id'], self.user_ticket.id)
        self.assertEqual(data['title'], 'User Ticket')
    
    def test_get_single_ticket_assignee(self):
        """Test getting a single ticket as the assignee."""
        # Login as assignee
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/tickets/{self.assigned_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['id'], self.assigned_ticket.id)
        self.assertEqual(data['title'], 'Assigned Ticket')
    
    def test_get_single_ticket_unauthorized(self):
        """Test getting a ticket without proper access."""
        # Login as user who doesn't own or isn't assigned to the ticket
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get(f'/api/tickets/{self.other_user_ticket.id}')
        self.assertEqual(response.status_code, 403)
    
    def test_get_single_ticket_admin(self):
        """Test getting any ticket as admin."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.get(f'/api/tickets/{self.other_user_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['id'], self.other_user_ticket.id)
    
    def test_update_ticket_owner(self):
        """Test updating a ticket as the owner."""
        # Login as ticket owner
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        update_data = {
            'title': 'Updated User Ticket',
            'status': 'in_progress',
            'priority': 'high'
        }
        
        response = self.client.put(f'/api/tickets/{self.user_ticket.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['title'], 'Updated User Ticket')
        self.assertEqual(data['status'], 'in_progress')
        self.assertEqual(data['priority'], 'high')
    
    def test_update_ticket_assignee(self):
        """Test updating a ticket as the assignee."""
        # Login as assignee
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        update_data = {
            'status': 'in_progress'
        }
        
        response = self.client.put(f'/api/tickets/{self.assigned_ticket.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['status'], 'in_progress')
    
    def test_update_ticket_unauthorized(self):
        """Test updating a ticket without proper access."""
        # Login as user who doesn't own or isn't assigned to the ticket
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        update_data = {
            'title': 'Unauthorized Update'
        }
        
        response = self.client.put(f'/api/tickets/{self.other_user_ticket.id}', json=update_data)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_ticket_admin(self):
        """Test deleting a ticket as admin."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.delete(f'/api/tickets/{self.user_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['message'], 'Ticket deleted successfully')
        
        # Verify ticket was deleted
        ticket = Ticket.query.get(self.user_ticket.id)
        self.assertIsNone(ticket)
    
    def test_delete_ticket_non_admin(self):
        """Test deleting a ticket as non-admin user."""
        # Login as regular user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.delete(f'/api/tickets/{self.user_ticket.id}')
        self.assertEqual(response.status_code, 403)
    
    def test_assign_ticket_admin(self):
        """Test assigning a ticket as admin."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        assign_data = {
            'assigned_to': self.admin.id
        }
        
        response = self.client.put(f'/api/tickets/admin/assign/{self.user_ticket.id}', 
                                 json=assign_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['assigned_to'], self.admin.id)
    
    def test_assign_ticket_to_non_admin(self):
        """Test assigning a ticket to a non-admin user."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        assign_data = {
            'assigned_to': self.user.id  # Regular user, not admin
        }
        
        response = self.client.put(f'/api/tickets/admin/assign/{self.user_ticket.id}', 
                                 json=assign_data)
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertEqual(data['error'], 'Can only assign tickets to admin users')
    
    def test_get_admin_users(self):
        """Test getting admin users for assignment."""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin.id
        
        response = self.client.get('/api/tickets/admin/users')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(user['username'] == 'admin' for user in data))
        self.assertFalse(any(user['username'] == 'testuser' for user in data))


class TestTicketsRoutesEdgeCases(unittest.TestCase):
    """Test edge cases for tickets routes."""
    
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
    
    def test_get_nonexistent_ticket(self):
        """Test getting a non-existent ticket."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.get('/api/tickets/999')
        self.assertEqual(response.status_code, 404)
    
    def test_update_nonexistent_ticket(self):
        """Test updating a non-existent ticket."""
        # Login as user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
        
        response = self.client.put('/api/tickets/999', json={'title': 'Updated'})
        self.assertEqual(response.status_code, 404)
    
    def test_delete_nonexistent_ticket(self):
        """Test deleting a non-existent ticket."""
        # Login as admin
        admin = create_test_user(username="admin", email="admin@example.com", is_admin=True)
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = admin.id
        
        response = self.client.delete('/api/tickets/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
