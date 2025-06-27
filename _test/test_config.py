"""
Test configuration and setup script for the ticketing system.
"""
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Test environment configuration
TEST_DATABASE_URI = 'sqlite:///:memory:'
TEST_SECRET_KEY = 'test-secret-key'

# Test data configuration
TEST_USERS = [
    {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': False
    },
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'adminpass123',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_admin': True
    }
]

TEST_TICKETS = [
    {
        'title': 'Test Ticket 1',
        'description': 'This is a test ticket',
        'priority': 'medium',
        'status': 'open'
    },
    {
        'title': 'Test Ticket 2',
        'description': 'Another test ticket',
        'priority': 'high',
        'status': 'in_progress'
    }
]


def setup_test_environment():
    """Set up the test environment."""
    # Set environment variables for testing
    os.environ['TESTING'] = 'True'
    os.environ['SECRET_KEY'] = TEST_SECRET_KEY
    os.environ['DATABASE_URL'] = TEST_DATABASE_URI
    
    print("Test environment configured successfully!")


def print_test_info():
    """Print information about the test suite."""
    print("="*60)
    print("TICKETING SYSTEM TEST SUITE")
    print("="*60)
    print()
    print("Test modules available:")
    print("  - models_test.py         : Test database models")
    print("  - auth_utils_test.py     : Test authentication utilities")
    print("  - auth_routes_test.py    : Test authentication routes")
    print("  - tickets_routes_test.py : Test ticket management routes")
    print("  - users_routes_test.py   : Test user management routes")
    print("  - main_test.py           : Test main application functionality")
    print("  - integration_test.py    : Test end-to-end workflows")
    print()
    print("Usage examples:")
    print("  python run_tests.py                    # Run all tests")
    print("  python run_tests.py -m models_test     # Run model tests only")
    print("  python run_tests.py -l                 # List all test modules")
    print("  python run_tests.py -v 1               # Run with less verbose output")
    print()
    print("="*60)


if __name__ == '__main__':
    setup_test_environment()
    print_test_info()
