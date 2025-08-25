#!/usr/bin/env python3
"""Test runner script for Calculator Service."""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Calculator Service Test Runner")
    parser.add_argument(
        '--type',
        choices=['unit', 'integration', 'all'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run tests with coverage reporting'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Skip slow tests'
    )
    parser.add_argument(
        '--lint',
        action='store_true',
        help='Run code quality checks'
    )
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print("🧪 Calculator Service Test Suite")
    print(f"📁 Working directory: {script_dir}")
    
    success = True
    
    # Code quality checks
    if args.lint:
        print("\n🔍 Running code quality checks...")
        
        # Black formatting check
        black_cmd = ['black', '--check', '--diff', 'app/', 'tests/']
        if not run_command(black_cmd, "Black code formatting check"):
            print("💡 Run 'black app/ tests/' to fix formatting")
            success = False
        
        # Flake8 linting
        flake8_cmd = ['flake8', 'app/', 'tests/']
        if not run_command(flake8_cmd, "Flake8 linting"):
            success = False
    
    # Prepare pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend([
            '--cov=app',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-fail-under=80'
        ])
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append('-v')
    else:
        pytest_cmd.append('-q')
    
    # Filter tests by type
    if args.type == 'unit':
        pytest_cmd.extend(['-m', 'unit', 'tests/unit/'])
    elif args.type == 'integration':
        pytest_cmd.extend(['-m', 'integration', 'tests/integration/'])
    else:
        pytest_cmd.append('tests/')
    
    # Skip slow tests if requested
    if args.fast:
        pytest_cmd.extend(['-m', 'not slow'])
    
    # Run tests
    if not run_command(pytest_cmd, f"Calculator Service {args.type} tests"):
        success = False
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("💥 Some tests failed!")
        sys.exit(1)
    
    print(f"{'='*60}")


if __name__ == '__main__':
    main()