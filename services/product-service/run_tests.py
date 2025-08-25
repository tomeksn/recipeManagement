#!/usr/bin/env python3
"""Test runner script for the Product Service."""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run tests for Product Service')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--pattern', '-k', help='Run tests matching pattern')
    parser.add_argument('--no-cov', action='store_true', help='Skip coverage reporting')
    
    args = parser.parse_args()
    
    # Change to the service directory
    service_dir = Path(__file__).parent
    print(f"Running tests from: {service_dir}")
    
    # Build base pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append('-v')
    
    # Add pattern matching
    if args.pattern:
        pytest_cmd.extend(['-k', args.pattern])
    
    # Add coverage unless disabled
    if not args.no_cov:
        pytest_cmd.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov'
        ])
    
    # Determine which tests to run
    if args.unit:
        pytest_cmd.extend(['-m', 'unit', 'tests/unit/'])
        description = "Unit Tests"
    elif args.integration:
        pytest_cmd.extend(['-m', 'integration', 'tests/integration/'])
        description = "Integration Tests"
    else:
        pytest_cmd.append('tests/')
        description = "All Tests"
    
    # Run tests
    success = run_command(pytest_cmd, description)
    
    if success:
        print(f"\n✅ {description} completed successfully!")
        
        if not args.no_cov:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ {description} failed!")
        sys.exit(1)
    
    # Run additional checks if running all tests
    if not (args.unit or args.integration):
        print("\n" + "="*60)
        print("Running additional code quality checks...")
        print("="*60)
        
        # Type checking with mypy
        mypy_cmd = ['python', '-m', 'mypy', 'app', '--ignore-missing-imports']
        mypy_success = run_command(mypy_cmd, "Type Checking (mypy)")
        
        # Code formatting check with black
        black_cmd = ['python', '-m', 'black', '--check', '--diff', 'app', 'tests']
        black_success = run_command(black_cmd, "Code Formatting Check (black)")
        
        # Linting with flake8
        flake8_cmd = ['python', '-m', 'flake8', 'app', 'tests']
        flake8_success = run_command(flake8_cmd, "Code Linting (flake8)")
        
        if all([success, mypy_success, black_success, flake8_success]):
            print("\n🎉 All checks passed! Code is ready for production.")
        else:
            print("\n⚠️  Some checks failed. Please review the output above.")
            sys.exit(1)


if __name__ == '__main__':
    main()