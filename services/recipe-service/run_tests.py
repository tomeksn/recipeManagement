#!/usr/bin/env python3
"""Test runner script for Recipe Service.

This script provides convenient commands for running different types of tests
with appropriate configurations and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))


def run_command(cmd: list, description: str) -> int:
    """Run a command and return exit code."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Recipe Service Test Runner")
    parser.add_argument(
        'test_type',
        choices=['unit', 'integration', 'performance', 'all', 'fast', 'coverage'],
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--no-cov',
        action='store_true',
        help='Skip coverage reporting'
    )
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run tests in parallel'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Run specific test file'
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append('-vvs')
    else:
        pytest_cmd.append('-v')
    
    # Add parallel execution
    if args.parallel:
        pytest_cmd.extend(['-n', 'auto'])
    
    # Add coverage options
    if not args.no_cov and args.test_type in ['unit', 'integration', 'all', 'coverage']:
        pytest_cmd.extend([
            '--cov=app',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing'
        ])
    
    # Configure test selection based on type
    if args.test_type == 'unit':
        pytest_cmd.extend(['-m', 'unit or not (integration or performance or slow)'])
        pytest_cmd.append('tests/unit/')
        description = "Unit Tests"
        
    elif args.test_type == 'integration':
        pytest_cmd.extend(['-m', 'integration or not (unit or performance or slow)'])
        pytest_cmd.append('tests/integration/')
        description = "Integration Tests"
        
    elif args.test_type == 'performance':
        pytest_cmd.extend(['-m', 'performance'])
        pytest_cmd.append('tests/performance/')
        description = "Performance Tests"
        
    elif args.test_type == 'fast':
        pytest_cmd.extend(['-m', 'not (slow or performance)'])
        description = "Fast Tests (Unit + Integration)"
        
    elif args.test_type == 'coverage':
        pytest_cmd.extend([
            '--cov=app',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-fail-under=80',
            '-m', 'not (slow or performance)'
        ])
        description = "Coverage Tests"
        
    elif args.test_type == 'all':
        pytest_cmd.extend(['-m', 'not slow'])  # Exclude very slow tests by default
        description = "All Tests (excluding slow)"
    
    # Handle specific file
    if args.file:
        pytest_cmd.append(args.file)
        description += f" - File: {args.file}"
    
    # Run the tests
    exit_code = run_command(pytest_cmd, description)
    
    # Additional commands based on test type
    if args.test_type == 'coverage' and exit_code == 0:
        print(f"\n{'='*60}")
        print("Coverage report generated at: htmlcov/index.html")
        print("You can open it in your browser to view detailed coverage")
        print(f"{'='*60}")
    
    if args.test_type in ['performance'] and exit_code == 0:
        print(f"\n{'='*60}")
        print("Performance tests completed!")
        print("Check the output above for timing information")
        print(f"{'='*60}")
    
    return exit_code


def run_specific_test_suites():
    """Run specific test suites for CI/CD or detailed testing."""
    test_suites = {
        'models': {
            'cmd': ['python', '-m', 'pytest', 'tests/unit/test_recipe_models.py', '-v'],
            'description': 'Recipe Models Tests'
        },
        'repository': {
            'cmd': ['python', '-m', 'pytest', 'tests/unit/test_recipe_repository.py', '-v'],
            'description': 'Repository Tests'
        },
        'api': {
            'cmd': ['python', '-m', 'pytest', 'tests/integration/test_recipe_api.py', '-v'],
            'description': 'API Integration Tests'
        },
        'circular_deps': {
            'cmd': ['python', '-m', 'pytest', 'tests/unit/test_circular_dependencies.py', '-v'],
            'description': 'Circular Dependency Tests'
        },
        'hierarchy_perf': {
            'cmd': ['python', '-m', 'pytest', 'tests/performance/test_hierarchy_performance.py', '-v', '-m', 'not slow'],
            'description': 'Hierarchy Performance Tests'
        }
    }
    
    print("Available test suites:")
    for name, suite in test_suites.items():
        print(f"  {name}: {suite['description']}")
    
    return test_suites


if __name__ == '__main__':
    # Check if specific suite requested
    if len(sys.argv) > 1 and sys.argv[1] == 'suites':
        suites = run_specific_test_suites()
        sys.exit(0)
    
    exit_code = main()
    sys.exit(exit_code)