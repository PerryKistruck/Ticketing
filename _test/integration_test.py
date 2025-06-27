"""
Integration tests for the entire ticketing system.
"""
import unittest
from models import db, User, Ticket
from _test.conftest import create_test_app, create_test_user, create_test_ticket


class TestTicketingSystemIntegration(unittest.TestCase):
    """End-to-end integration tests for the ticketing system."""
    
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
    
    def test_complete_user_workflow(self):
        """Test complete user workflow: register, login, create ticket, manage ticket."""
        # 1. Register a new user
        register_data = {
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password': 'integration123',
            'first_name': 'Integration',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/auth/register', json=register_data)
        self.assertEqual(response.status_code, 201)
        
        # 2. Login
        login_data = {
            'username': 'integrationuser',
            'password': 'integration123'
        }
        
        response = self.client.post('/api/auth/login', json=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 3. Access profile
        response = self.client.get('/api/auth/profile',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        user_data = response.get_json()
        user_id = user_data['id']
        
        # 4. Create a ticket
        ticket_data = {
            'title': 'Integration Test Ticket',
            'description': 'This is an integration test ticket',
            'priority': 'high'
        }
        
        response = self.client.post('/api/tickets/', json=ticket_data)
        self.assertEqual(response.status_code, 201)
        ticket_response = response.get_json()
        ticket_id = ticket_response['id']
        
        # 5. Get tickets (should include the created ticket)
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)
        tickets = response.get_json()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]['title'], 'Integration Test Ticket')
        
        # 6. Update the ticket
        update_data = {
            'status': 'in_progress',
            'description': 'Updated description'
        }
        
        response = self.client.put(f'/api/tickets/{ticket_id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        updated_ticket = response.get_json()
        self.assertEqual(updated_ticket['status'], 'in_progress')
        self.assertEqual(updated_ticket['description'], 'Updated description')
        
        # 7. Get single ticket
        response = self.client.get(f'/api/tickets/{ticket_id}')
        self.assertEqual(response.status_code, 200)
        
        # 8. Get user's tickets
        response = self.client.get(f'/api/users/{user_id}/tickets')
        self.assertEqual(response.status_code, 200)
        user_tickets = response.get_json()
        self.assertEqual(len(user_tickets), 1)
        
        # 9. Update user profile
        profile_update = {
            'first_name': 'Updated Integration',
            'last_name': 'Updated User'
        }
        
        response = self.client.put(f'/api/users/{user_id}', json=profile_update)
        self.assertEqual(response.status_code, 200)
        
        # 10. Logout
        response = self.client.post('/api/auth/logout',
                                  headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        
        # 11. Try to access protected resource (should fail)
        response = self.client.get('/api/auth/profile',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
    
    def test_admin_workflow(self):
        """Test admin workflow: manage all tickets, assign tickets, manage users."""
        # Create regular user and admin
        user = create_test_user()
        admin = create_test_user(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        
        # Create some tickets
        user_ticket = create_test_ticket(
            title="User Ticket",
            user_id=user.id
        )
        
        # Login as admin
        login_data = {
            'username': 'admin',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/auth/login', json=login_data)
        self.assertEqual(response.status_code, 200)
        
        # Access admin dashboard (template route)
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        
        # Get all tickets (admin endpoint)
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 200)
        all_tickets = response.get_json()
        self.assertEqual(len(all_tickets), 1)
        
        # Get admin users for assignment
        response = self.client.get('/api/tickets/admin/users')
        self.assertEqual(response.status_code, 200)
        admin_users = response.get_json()
        self.assertTrue(any(u['username'] == 'admin' for u in admin_users))
        
        # Assign ticket to admin
        assign_data = {
            'assigned_to': admin.id
        }
        
        response = self.client.put(f'/api/tickets/admin/assign/{user_ticket.id}', 
                                 json=assign_data)
        self.assertEqual(response.status_code, 200)
        assigned_ticket = response.get_json()
        self.assertEqual(assigned_ticket['assigned_to'], admin.id)
        
        # Update any ticket (admin can update any ticket)
        update_data = {
            'status': 'closed',
            'priority': 'low'
        }
        
        response = self.client.put(f'/api/tickets/{user_ticket.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Delete ticket (admin only)
        response = self.client.delete(f'/api/tickets/{user_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify ticket was deleted
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 200)
        remaining_tickets = response.get_json()
        self.assertEqual(len(remaining_tickets), 0)
    
    def test_access_control_enforcement(self):
        """Test that access controls are properly enforced across the system."""
        # Create users
        user1 = create_test_user(username="user1", email="user1@example.com")
        user2 = create_test_user(username="user2", email="user2@example.com")
        admin = create_test_user(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        
        # Create tickets
        user1_ticket = create_test_ticket(
            title="User1 Ticket",
            user_id=user1.id
        )
        user2_ticket = create_test_ticket(
            title="User2 Ticket",
            user_id=user2.id
        )
        
        # Login as user1
        with self.client.session_transaction() as sess:
            sess['user_id'] = user1.id
        
        # User1 can access their own ticket
        response = self.client.get(f'/api/tickets/{user1_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        # User1 cannot access user2's ticket
        response = self.client.get(f'/api/tickets/{user2_ticket.id}')
        self.assertEqual(response.status_code, 403)
        
        # User1 cannot access admin endpoints
        response = self.client.get('/api/tickets/admin/all',
                                 headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 403)
        
        # User1 cannot delete tickets
        response = self.client.delete(f'/api/tickets/{user1_ticket.id}')
        self.assertEqual(response.status_code, 403)
        
        # User1 can only access their own profile
        response = self.client.get(f'/api/users/{user1.id}')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f'/api/users/{user2.id}')
        self.assertEqual(response.status_code, 403)
        
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = admin.id
        
        # Admin can access all tickets
        response = self.client.get(f'/api/tickets/{user1_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f'/api/tickets/{user2_ticket.id}')
        self.assertEqual(response.status_code, 200)
        
        # Admin can access admin endpoints
        response = self.client.get('/api/tickets/admin/all')
        self.assertEqual(response.status_code, 200)
        
        # Admin can delete tickets
        response = self.client.delete(f'/api/tickets/{user1_ticket.id}')
        self.assertEqual(response.status_code, 200)
    
    def test_data_consistency(self):
        """Test data consistency across operations."""
        # Create user and login
        user = create_test_user()
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = user.id
        
        # Create ticket
        ticket_data = {
            'title': 'Consistency Test Ticket',
            'description': 'Testing data consistency',
            'priority': 'medium'
        }
        
        response = self.client.post('/api/tickets/', json=ticket_data)
        self.assertEqual(response.status_code, 201)
        created_ticket = response.get_json()
        ticket_id = created_ticket['id']
        
        # Verify ticket appears in user's tickets
        response = self.client.get('/api/tickets/')
        tickets = response.get_json()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]['id'], ticket_id)
        
        # Verify ticket appears in user's ticket list
        response = self.client.get(f'/api/users/{user.id}/tickets')
        user_tickets = response.get_json()
        self.assertEqual(len(user_tickets), 1)
        self.assertEqual(user_tickets[0]['id'], ticket_id)
        
        # Update ticket and verify consistency
        update_data = {
            'title': 'Updated Consistency Test Ticket',
            'status': 'in_progress'
        }
        
        response = self.client.put(f'/api/tickets/{ticket_id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify update is reflected everywhere
        response = self.client.get(f'/api/tickets/{ticket_id}')
        single_ticket = response.get_json()
        self.assertEqual(single_ticket['title'], 'Updated Consistency Test Ticket')
        self.assertEqual(single_ticket['status'], 'in_progress')
        
        response = self.client.get('/api/tickets/')
        tickets = response.get_json()
        self.assertEqual(tickets[0]['title'], 'Updated Consistency Test Ticket')
        self.assertEqual(tickets[0]['status'], 'in_progress')


if __name__ == '__main__':
    unittest.main()
