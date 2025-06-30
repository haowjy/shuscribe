#!/usr/bin/env python3
"""
Test Runner for ShuScribe Database Tests

Provides easy commands to run different test suites with appropriate configurations.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str = "") -> int:
    """Run a command and return the exit code."""
    if description:
        print(f"\n🚀 {description}")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run ShuScribe database tests")
    parser.add_argument(
        "suite", 
        nargs="?", 
        default="all",
        choices=["all", "unit", "integration", "performance", "user", "story", "wiki", "workspace", "quick"],
        help="Test suite to run"
    )
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-slow", action="store_true", help="Skip slow tests")
    parser.add_argument("--no-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--no-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--failfast", "-x", action="store_true", help="Stop on first failure")
    parser.add_argument("--parallel", "-n", type=int, help="Run tests in parallel (requires pytest-xdist)")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add fail fast
    if args.failfast:
        cmd.append("-x")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=src/database", "--cov-report=html", "--cov-report=term"])
    
    # Build test markers
    markers = []
    if args.no_slow:
        markers.append("not slow")
    if args.no_integration:
        markers.append("not integration")
    if args.no_performance:
        markers.append("not performance")
    
    if markers:
        cmd.extend(["-m", " and ".join(markers)])
    
    # Select test suite
    if args.suite == "all":
        cmd.append("tests/test_database/")
    elif args.suite == "unit":
        cmd.extend([
            "tests/test_database/",
            "-m", "not integration and not performance"
        ])
    elif args.suite == "integration":
        cmd.extend([
            "tests/test_database/",
            "-m", "integration"
        ])
    elif args.suite == "performance":
        cmd.extend([
            "tests/test_database/",
            "-m", "performance or slow"
        ])
    elif args.suite == "user":
        cmd.append("tests/test_database/test_user_repository.py")
    elif args.suite == "story":
        cmd.append("tests/test_database/test_story_repository.py")
    elif args.suite == "wiki":
        cmd.append("tests/test_database/test_wiki_repository.py")
    elif args.suite == "workspace":
        cmd.append("tests/test_database/test_workspace_repository.py")
    elif args.suite == "quick":
        cmd.extend([
            "tests/test_database/",
            "-m", "not slow and not integration and not performance",
            "--tb=short"
        ])
    
    # Run the tests
    exit_code = run_command(cmd, f"Running {args.suite} tests")
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/")
            print("Open htmlcov/index.html in your browser to view detailed coverage")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 