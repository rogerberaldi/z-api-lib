#!/usr/bin/env python3
"""
Test runner script for zapi_async.

Provides convenient commands for running different test suites.
"""

import sys
import os
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"{Colors.BLUE}▶ {description}{Colors.END}")
    print(f"{Colors.YELLOW}  Command: {' '.join(cmd)}{Colors.END}\n")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n{Colors.GREEN}✅ {description} - PASSED{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.RED}❌ {description} - FAILED{Colors.END}\n")
        return False


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    if command == "unit":
        run_unit_tests()
    elif command == "webhook":
        run_webhook_tests()
    elif command == "helpers":
        run_helper_tests()
    elif command == "integration":
        run_integration_tests()
    elif command == "all":
        run_all_tests()
    elif command == "coverage":
        run_with_coverage()
    elif command == "fast":
        run_fast_tests()
    elif command == "verbose":
        run_verbose()
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.END}\n")
        print_usage()
        sys.exit(1)


def print_usage():
    """Print usage information."""
    print_header("Z-API Async Test Runner")
    
    print(f"{Colors.BOLD}Usage:{Colors.END}")
    print(f"  python run_tests.py <command>\n")
    
    print(f"{Colors.BOLD}Commands:{Colors.END}")
    print(f"  {Colors.GREEN}unit{Colors.END}         - Run unit tests only (fast, mocked)")
    print(f"  {Colors.GREEN}webhook{Colors.END}      - Run webhook parsing tests")
    print(f"  {Colors.GREEN}helpers{Colors.END}      - Run helper function tests")
    print(f"  {Colors.GREEN}integration{Colors.END}  - Run integration tests (requires credentials)")
    print(f"  {Colors.GREEN}all{Colors.END}          - Run all tests (except integration)")
    print(f"  {Colors.GREEN}fast{Colors.END}         - Run fast tests only (skip slow)")
    print(f"  {Colors.GREEN}coverage{Colors.END}     - Run with coverage report")
    print(f"  {Colors.GREEN}verbose{Colors.END}      - Run with maximum verbosity")
    
    print(f"\n{Colors.BOLD}Examples:{Colors.END}")
    print(f"  python run_tests.py unit")
    print(f"  python run_tests.py coverage")
    print(f"  python run_tests.py integration")
    
    print(f"\n{Colors.BOLD}Integration Tests:{Colors.END}")
    print(f"  Set environment variables:")
    print(f"    export ZAPI_INSTANCE_ID='your_instance'")
    print(f"    export ZAPI_TOKEN='your_token'")
    print(f"    export ZAPI_CLIENT_TOKEN='your_client_token'")
    print(f"    export ZAPI_TEST_PHONE='5511999999999'")


def run_unit_tests():
    """Run unit tests only."""
    print_header("Running Unit Tests")
    
    cmd = [
        "pytest",
        "tests/",
        "-m", "unit",
        "-v",
        "--tb=short"
    ]
    
    success = run_command(cmd, "Unit Tests")
    sys.exit(0 if success else 1)


def run_webhook_tests():
    """Run webhook tests."""
    print_header("Running Webhook Tests")
    
    cmd = [
        "pytest",
        "tests/test_webhooks.py",
        "-v",
        "--tb=short"
    ]
    
    success = run_command(cmd, "Webhook Tests")
    sys.exit(0 if success else 1)


def run_helper_tests():
    """Run helper function tests."""
    print_header("Running Helper Tests")
    
    cmd = [
        "pytest",
        "tests/test_helpers.py",
        "-v",
        "--tb=short"
    ]
    
    success = run_command(cmd, "Helper Function Tests")
    sys.exit(0 if success else 1)


def run_integration_tests():
    """Run integration tests."""
    print_header("Running Integration Tests")
    
    # Check for credentials
    required_vars = ["ZAPI_INSTANCE_ID", "ZAPI_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"{Colors.RED}❌ Missing environment variables: {', '.join(missing)}{Colors.END}")
        print(f"\n{Colors.YELLOW}Set credentials first:{Colors.END}")
        for var in missing:
            print(f"  export {var}='your_{var.lower()}'")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✓ Credentials found{Colors.END}")
    print(f"  Instance: {os.getenv('ZAPI_INSTANCE_ID')}")
    print(f"  Test Phone: {os.getenv('ZAPI_TEST_PHONE', 'Not set')}\n")
    
    print(f"{Colors.YELLOW}⚠️  WARNING: This will make REAL API calls!{Colors.END}")
    response = input("Continue? (yes/no): ")
    
    if response.lower() not in ["yes", "y"]:
        print("Aborted.")
        sys.exit(0)
    
    cmd = [
        "pytest",
        "tests/test_integration.py",
        "-v",
        "-s",
        "--tb=short",
        "-m", "integration"
    ]
    
    success = run_command(cmd, "Integration Tests")
    sys.exit(0 if success else 1)


def run_all_tests():
    """Run all tests except integration."""
    print_header("Running All Tests (Unit + Webhook)")
    
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", "not integration"
    ]
    
    success = run_command(cmd, "All Tests")
    sys.exit(0 if success else 1)


def run_fast_tests():
    """Run fast tests only."""
    print_header("Running Fast Tests")
    
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", "not slow and not integration"
    ]
    
    success = run_command(cmd, "Fast Tests")
    sys.exit(0 if success else 1)


def run_with_coverage():
    """Run tests with coverage report."""
    print_header("Running Tests with Coverage")
    
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=zapi_async",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-m", "not integration"
    ]
    
    success = run_command(cmd, "Tests with Coverage")
    
    if success:
        print(f"\n{Colors.GREEN}📊 Coverage report generated:{Colors.END}")
        print(f"  Open: htmlcov/index.html\n")
    
    sys.exit(0 if success else 1)


def run_verbose():
    """Run with maximum verbosity."""
    print_header("Running Tests (Verbose)")
    
    cmd = [
        "pytest",
        "tests/",
        "-vv",
        "-s",
        "--tb=long",
        "--log-cli-level=DEBUG",
        "-m", "not integration"
    ]
    
    success = run_command(cmd, "Verbose Tests")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.END}\n")
        sys.exit(130)
