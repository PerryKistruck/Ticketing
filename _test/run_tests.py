"""
Test runner for the ticketing system.
Run all tests or specific test modules.
"""
import os
import sys
import unittest
import argparse

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def discover_and_run_tests(test_dir=None, pattern='*_test.py', verbosity=2):
    """
    Discover and run all tests in the specified directory.
    
    Args:
        test_dir (str): Directory to search for tests (default: current directory)
        pattern (str): Pattern to match test files (default: '*_test.py')
        verbosity (int): Test output verbosity level (default: 2)
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    if test_dir is None:
        test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_module, test_class=None, test_method=None, verbosity=2):
    """
    Run a specific test module, class, or method.
    
    Args:
        test_module (str): Name of the test module (without .py extension)
        test_class (str): Name of the test class (optional)
        test_method (str): Name of the test method (optional)
        verbosity (int): Test output verbosity level (default: 2)
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Import the test module
    try:
        module = __import__(test_module)
    except ImportError as e:
        print(f"Error importing test module '{test_module}': {e}")
        return False
    
    # Build the test suite
    loader = unittest.TestLoader()
    
    if test_method and test_class:
        # Run specific test method
        suite = loader.loadTestsFromName(f"{test_class}.{test_method}", module)
    elif test_class:
        # Run specific test class
        suite = loader.loadTestsFromName(test_class, module)
    else:
        # Run all tests in the module
        suite = loader.loadTestsFromModule(module)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(description='Test runner for the ticketing system')
    
    parser.add_argument(
        '--module', '-m',
        help='Run tests from a specific module (e.g., models_test, auth_routes_test)'
    )
    
    parser.add_argument(
        '--class', '-c',
        dest='test_class',
        help='Run tests from a specific test class'
    )
    
    parser.add_argument(
        '--method', '-t',
        dest='test_method',
        help='Run a specific test method'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*_test.py',
        help='Pattern to match test files (default: *_test.py)'
    )
    
    parser.add_argument(
        '--verbosity', '-v',
        type=int,
        default=2,
        choices=[0, 1, 2],
        help='Test output verbosity level (0=quiet, 1=normal, 2=verbose)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available test modules'
    )
    
    args = parser.parse_args()
    
    # List available test modules
    if args.list:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_files = [f for f in os.listdir(test_dir) if f.endswith('_test.py')]
        print("Available test modules:")
        for test_file in sorted(test_files):
            module_name = test_file[:-3]  # Remove .py extension
            print(f"  {module_name}")
        return
    
    # Run specific test or discover all tests
    if args.module:
        success = run_specific_test(
            args.module,
            args.test_class,
            args.test_method,
            args.verbosity
        )
    else:
        success = discover_and_run_tests(
            pattern=args.pattern,
            verbosity=args.verbosity
        )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
