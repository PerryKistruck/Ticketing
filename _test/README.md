# Test Suite Documentation

Comprehensive unit and integration tests for the ticketing system application.

## Test Modules

- `models_test.py` - Database model validation
- `auth_utils_test.py` - Authentication utility functions
- `auth_routes_test.py` - Authentication API endpoints
- `tickets_routes_test.py` - Ticket management API endpoints
- `users_routes_test.py` - User management API endpoints
- `main_test.py` - Main application routes
- `integration_test.py` - End-to-end workflows

## Configuration

- `conftest.py` - Test utilities and fixtures
- `test_config.py` - Test environment configuration
- `run_tests.py` - Test execution script

## Execution

### Command Line
```bash
python run_tests.py                           # All tests
python run_tests.py -m models_test            # Specific module
python run_tests.py -m models_test -c TestUser # Specific class
python run_tests.py --list                    # List modules
python run_tests.py -v 2                      # Verbose output
```

### Windows Batch
```cmd
test.bat                # All tests
test.bat models_test    # Specific module
test.bat list           # List modules
```

## Coverage Summary

**Total Tests**: 110 (104 passing, 6 skipped)

### Functional Areas
- User authentication and session management
- Ticket CRUD operations and access control
- Administrative functionality and permissions
- Database models and relationships
- API endpoints (JSON) and form submissions
- Error handling and security validation

### Test Categories
- **Models**: User/Ticket creation, validation, relationships
- **Authentication**: Login/logout, decorators, session handling
- **API Routes**: CRUD operations, access control, error responses
- **Integration**: Complete workflows, cross-module functionality
- **Security**: Authorization, session validation, access prevention
## Development Guidelines

### Test Structure
```python
class TestExample(unittest.TestCase):
    def setUp(self):
        # Initialize test fixtures
        
    def tearDown(self):
        # Clean up resources
        
    def test_functionality(self):
        # Arrange, Act, Assert pattern
```

### Best Practices
- Maintain test isolation and independence
- Use descriptive naming conventions
- Test both success and failure scenarios
- Validate access control and security
- Include edge cases and error conditions

## Configuration

- **Database**: SQLite in-memory (`:memory:`)
- **Framework**: Python unittest module
- **Utilities**: Custom helper functions for user/ticket creation
- **Authentication**: Session-based testing helpers

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
