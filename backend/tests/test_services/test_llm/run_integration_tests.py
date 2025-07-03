#!/usr/bin/env python3
"""
LLM Service Integration Test Runner

This script provides a simple way to run LLM integration tests with proper setup.
It's an alternative to using pytest commands directly.

Usage:
    python run_integration_tests.py [--provider PROVIDER] [--verbose]

Examples:
    python run_integration_tests.py                    # Run all integration tests
    python run_integration_tests.py --provider openai  # Test only OpenAI
    python run_integration_tests.py --verbose          # Verbose output
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_prerequisites():
    """Check if prerequisites are met before running tests."""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not (Path.cwd() / "src").exists():
        print("❌ Please run this script from the backend directory")
        return False
    
    # Check for .env file
    if not Path(".env").exists():
        print("❌ Missing .env file - please create one with your API keys")
        return False
    
    # Check for Portkey Gateway
    try:
        import httpx
        response = httpx.get("http://localhost:8787/", timeout=5.0)
        if response.status_code == 200:
            print("✅ Portkey Gateway is running")
        else:
            print("❌ Portkey Gateway not responding properly")
            return False
    except Exception:
        print("❌ Portkey Gateway not running at http://localhost:8787")
        print("   Start it with: docker run -d --name portkey-gateway -p 8787:8787 portkeyai/gateway:latest")
        return False
    
    # Check for API keys
    from dotenv import dotenv_values
    env_values = dotenv_values()
    
    api_keys = {
        "OPENAI_API_KEY": env_values.get("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": env_values.get("GOOGLE_API_KEY"),
        "ANTHROPIC_API_KEY": env_values.get("ANTHROPIC_API_KEY")
    }
    
    available_keys = [k for k, v in api_keys.items() if v]
    if not available_keys:
        print("❌ No API keys found in .env file")
        return False
    
    print(f"✅ Found API keys: {', '.join(available_keys)}")
    return True


def run_tests(provider=None, verbose=False):
    """Run the integration tests with specified options."""
    
    # Base pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "-m", "integration",
        "tests/test_services/test_llm/"
    ]
    
    # Add verbose flag if requested
    if verbose:
        cmd.extend(["-v", "-s"])
    
    # Add provider-specific test if requested
    if provider:
        provider_test = (
            f"tests/test_services/test_llm/test_llm_service_integration.py::"
            f"TestLLMServiceIntegration::test_chat_completion_per_provider[{provider}]"
        )
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "integration",
            provider_test
        ]
        if verbose:
            cmd.extend(["-v", "-s"])
    
    print(f"🚀 Running command: {' '.join(cmd)}")
    print("=" * 50)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run LLM Service Integration Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_integration_tests.py                    # Run all integration tests
  python run_integration_tests.py --provider openai  # Test only OpenAI
  python run_integration_tests.py --verbose          # Verbose output
  python run_integration_tests.py --provider google --verbose  # Google tests with verbose output
        """
    )
    
    parser.add_argument(
        "--provider",
        choices=["openai", "google", "anthropic"],
        help="Test only a specific provider"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    print("🧪 LLM Service Integration Test Runner")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    print("\n🎯 Prerequisites met! Starting tests...")
    
    # Run tests
    success = run_tests(provider=args.provider, verbose=args.verbose)
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 