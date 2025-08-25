#!/usr/bin/env python3
"""Test runner script for API Gateway."""
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
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure all required tools are installed")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="API Gateway Test Runner")
    parser.add_argument(
        '--type',
        choices=['all', 'unit', 'integration', 'lint', 'coverage'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--no-coverage',
        action='store_true',
        help='Skip coverage reporting'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🔧 API Gateway Test Suite")
    print(f"📁 Working directory: {Path.cwd()}")
    
    success = True
    
    # Determine which tests to run
    run_lint = args.type in ['all', 'lint']
    run_unit = args.type in ['all', 'unit']
    run_integration = args.type in ['all', 'integration'] 
    run_coverage = args.type == 'coverage' or (args.type == 'all' and not args.no_coverage)
    
    # Build pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        pytest_cmd.append('-v')
    else:
        pytest_cmd.append('-q')
    
    # Code quality checks
    if run_lint:
        # Black formatting check
        black_cmd = ['python', '-m', 'black', '--check', '--diff', 'app/', 'tests/']
        if not run_command(black_cmd, "Black code formatting check"):
            print("💡 Run 'python -m black app/ tests/' to fix formatting")
            success = False
        
        # Flake8 linting
        flake8_cmd = ['python', '-m', 'flake8', 'app/', 'tests/', '--max-line-length=100']
        if not run_command(flake8_cmd, "Flake8 linting"):
            success = False
    
    # Unit tests
    if run_unit:
        unit_cmd = pytest_cmd + ['tests/unit/']
        if not run_command(unit_cmd, f"API Gateway unit tests"):
            success = False
    
    # Integration tests
    if run_integration:
        integration_cmd = pytest_cmd + ['tests/integration/']
        if not run_command(integration_cmd, f"API Gateway integration tests"):
            success = False
    
    # Coverage report
    if run_coverage:
        coverage_cmd = pytest_cmd + [
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=80',
            'tests/'
        ]
        if not run_command(coverage_cmd, "API Gateway tests with coverage"):
            success = False
        else:
            print("📊 Coverage report generated in htmlcov/index.html")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests passed!")
        print("✅ API Gateway is ready for deployment")
    else:
        print("💥 Some tests failed!")
        print("❌ Please fix the issues before proceeding")
        sys.exit(1)
    
    print(f"{'='*60}")


if __name__ == '__main__':
    main()