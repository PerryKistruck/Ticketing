# Ticketing System Test Suite

This directory contains comprehensive unit tests for the ticketing system web application.

## Test Structure

The test suite is organized into the following modules:

- **`models_test.py`** - Tests for database models (User, Ticket)
- **`auth_utils_test.py`** - Tests for authentication utilities and decorators
- **`auth_routes_test.py`** - Tests for authentication API routes
- **`tickets_routes_test.py`** - Tests for ticket management API routes
- **`users_routes_test.py`** - Tests for user management API routes  
- **`main_test.py`** - Tests for main application routes and functionality
- **`integration_test.py`** - End-to-end integration tests

## Test Configuration

- **`conftest.py`** - Test configuration and utility functions
- **`test_config.py`** - Test environment setup and configuration
- **`run_tests.py`** - Test runner script with command-line options

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Module
```bash
python run_tests.py -m models_test
python run_tests.py -m auth_routes_test
```

### Run Specific Test Class
```bash
python run_tests.py -m models_test -c TestUser
```

### Run Specific Test Method
```bash
python run_tests.py -m models_test -c TestUser -t test_user_creation
```

### List Available Test Modules
```bash
python run_tests.py --list
```

### Adjust Verbosity
```bash
python run_tests.py -v 0  # Quiet
python run_tests.py -v 1  # Normal
python run_tests.py -v 2  # Verbose (default)
```

## Windows Batch Script

For convenience on Windows, use the batch script:

```cmd
test.bat                # Run all tests
test.bat models_test    # Run specific module
test.bat list           # List available modules
test.bat help           # Show help
```

## Test Coverage

The test suite covers:

### Models (9 tests)
- User creation and validation
- Password hashing and verification
- User serialization (to_dict)
- Ticket creation and relationships
- Database constraints and validation

### Authentication Utilities (12 tests)
- `get_current_user()` function
- `@login_required` decorator
- `@admin_required` decorator
- Session handling and validation
- Access control enforcement

### Authentication Routes (21 tests)
- User registration (JSON and form)
- User login/logout (JSON and form)
- Profile access and management
- Session persistence
- Error handling and edge cases

### Ticket Routes (23 tests)
- Ticket creation, reading, updating, deletion
- Access control (owner, assignee, admin)
- Admin-only endpoints
- Ticket assignment and filtering
- Error handling for invalid requests

### User Routes (24 tests)  
- User CRUD operations
- Profile management
- Access control enforcement
- User ticket listings
- Data validation

### Main Application (17 tests)
- Route registration and functionality
- Template rendering (basic)
- Admin dashboard access control
- Error handling and security
- Database initialization

### Integration Tests (4 tests)
- Complete user workflow (register → login → create ticket → manage → logout)
- Admin workflow (manage all tickets, assignments)
- End-to-end access control enforcement
- Data consistency across operations

## Test Database

Tests use an in-memory SQLite database (`sqlite:///:memory:`) for:
- Fast execution
- Isolation between tests
- No external dependencies
- Automatic cleanup

## Key Features

### Authentication Testing
- Session-based authentication
- Role-based access control (admin vs user)
- JSON API and form-based endpoints
- Password hashing validation

### API Testing
- RESTful API endpoints
- JSON request/response handling
- HTTP status code validation
- Error message verification

### Data Integrity
- Model relationships and constraints
- Database operations (CRUD)
- Transaction handling
- Data serialization

### Security Testing
- Access control enforcement
- Invalid session handling
- SQL injection protection
- Cross-user data access prevention

## Test Utilities

### Helper Functions
- `create_test_user()` - Create test users with various roles
- `create_test_ticket()` - Create test tickets with relationships
- `login_user()` / `logout_user()` - Authentication helpers
- `create_test_app()` - Configured test Flask application

### Test Configuration
- Isolated test database
- Test-specific configuration
- Mock template rendering
- Session management

## Notes

### Skipped Tests
Some tests are skipped because they require HTML templates that are not included in the test environment. These tests focus on API functionality rather than template rendering.

### Database Relationships
Tests verify proper functioning of SQLAlchemy relationships between Users and Tickets, including cascade deletions and foreign key constraints.

### Error Handling
Comprehensive testing of error conditions including:
- Invalid authentication
- Missing required fields
- Access control violations
- Non-existent resources
- Malformed requests

## Test Statistics

- **Total Tests**: 110
- **Passing**: 104
- **Skipped**: 6 (template-based tests)
- **Failed**: 0

The test suite provides excellent coverage of the application's core functionality and ensures reliable operation of the ticketing system.

The test suite is organized into the following modules:

### Core Tests
- **`models_test.py`** - Tests for database models (User, Ticket)
  - User model creation, validation, and relationships
  - Ticket model creation, validation, and relationships
  - Password hashing and verification
  - Model serialization methods

- **`auth_utils_test.py`** - Tests for authentication utilities
  - Login required decorator
  - Admin required decorator
  - Current user retrieval
  - Session management

- **`auth_routes_test.py`** - Tests for authentication routes
  - User registration (API and form)
  - User login/logout (API and form)
  - Profile access and management
  - Session persistence

### API Route Tests
- **`tickets_routes_test.py`** - Tests for ticket management routes
  - Ticket creation, retrieval, updating, deletion
  - Access control (owner, assignee, admin)
  - Admin ticket assignment and management
  - Filtering and querying

- **`users_routes_test.py`** - Tests for user management routes
  - User profile management
  - Access control enforcement
  - User ticket retrieval
  - Account deletion

### Application Tests
- **`main_test.py`** - Tests for main application functionality
  - Template routes (home, dashboard, admin)
  - Route registration and configuration
  - Error handling and security
  - Database initialization

### Integration Tests
- **`integration_test.py`** - End-to-end workflow tests
  - Complete user workflows
  - Admin management workflows
  - Access control enforcement
  - Data consistency across operations

## Running Tests

### Quick Start

#### Using the Batch File (Windows)
```batch
# Run all tests
test.bat

# Run specific module tests
test.bat models_test

# List available test modules
test.bat list

# Get help
test.bat help
```

#### Using Python Directly
```bash
# Run all tests
python run_tests.py

# Run specific module tests
python run_tests.py --module models_test

# Run specific test class
python run_tests.py --module models_test --class TestUser

# Run specific test method
python run_tests.py --module models_test --class TestUser --method test_user_creation

# List available test modules
python run_tests.py --list

# Run with different verbosity levels
python run_tests.py --verbosity 1  # Less verbose
python run_tests.py --verbosity 2  # More verbose (default)
```

### Test Configuration

The test suite uses an in-memory SQLite database by default for fast, isolated testing. Configuration is handled in `conftest.py` and `test_config.py`.

#### Test Database
- **Type**: SQLite in-memory database
- **Benefits**: Fast, isolated, no cleanup required
- **Location**: `:memory:`

#### Test Data
Tests use factory functions to create consistent test data:
- `create_test_user()` - Creates test users
- `create_test_ticket()` - Creates test tickets
- `login_user()` / `logout_user()` - Helper functions for authentication

## Test Coverage

The test suite covers:

### Functional Areas
- ✅ User registration and authentication
- ✅ Session management and security
- ✅ Ticket creation, modification, and deletion
- ✅ Access control and permissions
- ✅ Admin functionality
- ✅ API endpoints (JSON responses)
- ✅ Form submissions (redirects and flash messages)
- ✅ Database relationships and constraints
- ✅ Error handling and edge cases

### Security Testing
- ✅ Authentication required for protected routes
- ✅ Admin-only access enforcement
- ✅ Cross-user access prevention
- ✅ Session security
- ✅ SQL injection protection (basic)

### Integration Testing
- ✅ Complete user workflows
- ✅ Admin management workflows
- ✅ Data consistency across operations
- ✅ Cross-module functionality

## Requirements

The test suite requires the following dependencies (already included in the main project):

```
Flask>=3.1.1
Flask-SQLAlchemy>=3.1.1
Werkzeug>=3.1.3
```

No additional testing frameworks are required - the suite uses Python's built-in `unittest` module.

## Development Guidelines

### Adding New Tests

1. **Choose the appropriate test module** based on what you're testing
2. **Follow the naming convention**: `test_[functionality]` for test methods
3. **Use descriptive test names** that explain what is being tested
4. **Include docstrings** explaining the test purpose
5. **Follow the AAA pattern**: Arrange, Act, Assert

### Test Structure

Each test module follows this structure:

```python
class TestSomething(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test app, database, users, etc.
        
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up database, app context, etc.
        
    def test_specific_functionality(self):
        """Test a specific piece of functionality."""
        # Arrange: Set up test data
        # Act: Perform the action being tested
        # Assert: Verify the results
```

### Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Clean State**: Use `setUp()` and `tearDown()` to ensure clean test state
3. **Descriptive Names**: Test names should clearly indicate what is being tested
4. **Edge Cases**: Include tests for edge cases and error conditions
5. **Access Control**: Always test both authorized and unauthorized access
6. **Data Validation**: Test both valid and invalid data inputs

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running tests from the project root directory
2. **Database Errors**: The test suite creates its own in-memory database, so this shouldn't be an issue
3. **Authentication Issues**: Make sure you're using the test helper functions for login/logout
4. **Path Issues**: Use absolute paths in file operations

### Running Individual Tests

If you need to debug a specific test, you can run it directly:

```python
# Run a specific test file
python -m unittest _test.models_test

# Run a specific test class
python -m unittest _test.models_test.TestUser

# Run a specific test method
python -m unittest _test.models_test.TestUser.test_user_creation
```

### Debug Mode

For debugging, you can add print statements or use the Python debugger:

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

## Contributing

When adding new features to the main application:

1. **Write tests first** (TDD approach) or alongside the feature
2. **Test both success and failure cases**
3. **Include integration tests** for complex workflows
4. **Update this README** if you add new test modules or significantly change the structure
5. **Run the full test suite** before submitting changes

## Test Results

A successful test run should show output similar to:

```
Ran 89 tests in 2.145s

OK
```

Failed tests will show detailed error information including:
- Which test failed
- The assertion that failed
- The actual vs. expected values
- Stack trace for debugging
