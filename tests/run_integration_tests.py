#!/usr/bin/env python
"""
Script to run integration tests for the unreal-blender-mcp system.
"""

import os
import sys
import unittest
import argparse
import logging
from typing import List, Optional

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def run_tests(test_pattern: Optional[str] = None, verbose: bool = False) -> int:
    """
    Run the integration tests.
    
    Args:
        test_pattern: Optional pattern to filter tests.
        verbose: Whether to enable verbose output.
        
    Returns:
        int: The number of test failures.
    """
    # Set up logging
    setup_logging(verbose)
    
    # Create a test suite
    loader = unittest.TestLoader()
    
    if test_pattern:
        # Run specific tests
        suite = loader.loadTestsFromName(f'integration.test_integration.IntegrationTests.{test_pattern}')
    else:
        # Run all tests
        suite = loader.discover('tests/integration', pattern='test_*.py')
    
    # Run the tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return the number of failures
    return len(result.failures) + len(result.errors)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run integration tests for unreal-blender-mcp')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-t', '--test', help='Run a specific test (e.g., test_blender_connection)')
    
    args = parser.parse_args()
    
    # Print header
    print('=' * 80)
    print('Unreal-Blender-MCP Integration Tests')
    print('=' * 80)
    
    # Run the tests
    failures = run_tests(args.test, args.verbose)
    
    # Exit with the number of failures
    sys.exit(failures)

if __name__ == '__main__':
    main() 