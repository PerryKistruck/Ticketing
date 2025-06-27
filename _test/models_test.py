"""
Unit tests for the models module.
"""
import unittest
from datetime import datetime
from werkzeug.security import check_password_hash
from models import db, User, Ticket
from _test.conftest import create_test_app, TestConfig


class TestUser(unittest.TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test creating a new user."""
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        user.set_password("testpass123")
        
        db.session.add(user)
        db.session.commit()
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.created_at)
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        password = "testpass123"
        user.set_password(password)
        
        # Password should be hashed
        self.assertNotEqual(user.password_hash, password)
        self.assertTrue(check_password_hash(user.password_hash, password))
        
        # Check password method should work
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password("wrongpassword"))
    
    def test_user_to_dict(self):
        """Test user serialization to dictionary."""
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_admin=True
        )
        user.set_password("testpass123")
        
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        
        self.assertEqual(user_dict['username'], "testuser")
        self.assertEqual(user_dict['email'], "test@example.com")
        self.assertEqual(user_dict['first_name'], "Test")
        self.assertEqual(user_dict['last_name'], "User")
        self.assertTrue(user_dict['is_admin'])
        self.assertTrue(user_dict['is_active'])
        self.assertIsNotNone(user_dict['id'])
        self.assertIsNotNone(user_dict['created_at'])
        self.assertNotIn('password_hash', user_dict)
    
    def test_unique_constraints(self):
        """Test that username and email are unique."""
        user1 = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        user1.set_password("testpass123")
        
        db.session.add(user1)
        db.session.commit()
        
        # Try to create another user with same username
        user2 = User(
            username="testuser",
            email="different@example.com",
            first_name="Another",
            last_name="User"
        )
        user2.set_password("testpass123")
        
        db.session.add(user2)
        
        with self.assertRaises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # Try to create another user with same email
        user3 = User(
            username="differentuser",
            email="test@example.com",
            first_name="Another",
            last_name="User"
        )
        user3.set_password("testpass123")
        
        db.session.add(user3)
        
        with self.assertRaises(Exception):
            db.session.commit()


class TestTicket(unittest.TestCase):
    """Test cases for the Ticket model."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test users
        self.user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        self.user.set_password("testpass123")
        
        self.admin = User(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.admin.set_password("adminpass123")
        
        db.session.add(self.user)
        db.session.add(self.admin)
        db.session.commit()
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_ticket_creation(self):
        """Test creating a new ticket."""
        ticket = Ticket(
            title="Test Ticket",
            description="This is a test ticket",
            user_id=self.user.id,
            status="open",
            priority="high"
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        self.assertIsNotNone(ticket.id)
        self.assertEqual(ticket.title, "Test Ticket")
        self.assertEqual(ticket.description, "This is a test ticket")
        self.assertEqual(ticket.user_id, self.user.id)
        self.assertEqual(ticket.status, "open")
        self.assertEqual(ticket.priority, "high")
        self.assertIsNone(ticket.assigned_to)
        self.assertIsNotNone(ticket.created_at)
        self.assertIsNotNone(ticket.updated_at)
    
    def test_ticket_default_values(self):
        """Test ticket default values."""
        ticket = Ticket(
            title="Test Ticket",
            user_id=self.user.id
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        self.assertEqual(ticket.status, "open")
        self.assertEqual(ticket.priority, "medium")
    
    def test_ticket_assignment(self):
        """Test ticket assignment to admin."""
        ticket = Ticket(
            title="Test Ticket",
            description="This is a test ticket",
            user_id=self.user.id,
            assigned_to=self.admin.id
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        self.assertEqual(ticket.assigned_to, self.admin.id)
        self.assertEqual(ticket.assignee, self.admin)
    
    def test_ticket_to_dict(self):
        """Test ticket serialization to dictionary."""
        ticket = Ticket(
            title="Test Ticket",
            description="This is a test ticket",
            user_id=self.user.id,
            assigned_to=self.admin.id,
            status="in_progress",
            priority="high"
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        ticket_dict = ticket.to_dict()
        
        self.assertEqual(ticket_dict['title'], "Test Ticket")
        self.assertEqual(ticket_dict['description'], "This is a test ticket")
        self.assertEqual(ticket_dict['user_id'], self.user.id)
        self.assertEqual(ticket_dict['assigned_to'], self.admin.id)
        self.assertEqual(ticket_dict['status'], "in_progress")
        self.assertEqual(ticket_dict['priority'], "high")
        self.assertEqual(ticket_dict['assignee_name'], "Admin User")
        self.assertEqual(ticket_dict['user_name'], "Test User")
        self.assertIsNotNone(ticket_dict['id'])
        self.assertIsNotNone(ticket_dict['created_at'])
        self.assertIsNotNone(ticket_dict['updated_at'])
    
    def test_ticket_relationships(self):
        """Test ticket relationships with users."""
        ticket = Ticket(
            title="Test Ticket",
            description="This is a test ticket",
            user_id=self.user.id,
            assigned_to=self.admin.id
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Test user relationship
        self.assertEqual(ticket.user, self.user)
        self.assertIn(ticket, self.user.tickets)
        
        # Test assignee relationship
        self.assertEqual(ticket.assignee, self.admin)
        self.assertIn(ticket, self.admin.assigned_tickets)


if __name__ == '__main__':
    unittest.main()
