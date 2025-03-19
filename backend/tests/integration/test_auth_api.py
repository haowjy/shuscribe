# tests/integration/test_auth_api.py
import pytest
import requests
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.test'))

# Constants - can be overridden by environment variables
API_URL = os.getenv("TEST_API_URL", "http://localhost:8000/api")

@pytest.fixture
def supabase_token():
    """Get a valid Supabase token for testing"""
    token = os.getenv("TEST_SUPABASE_TOKEN")
    if not token:
        pytest.skip("TEST_SUPABASE_TOKEN environment variable not set")
    return token

@pytest.fixture
def llm_api_key():
    """Get a valid LLM API key for testing"""
    key = os.getenv("TEST_LLM_API_KEY")
    if not key:
        pytest.skip("TEST_LLM_API_KEY environment variable not set")
    return key

def test_auth_endpoint(supabase_token):
    """Test that the auth endpoint returns user data with a valid token"""
    response = requests.get(
        f"{API_URL}/auth/me",
        headers={"Authorization": f"Bearer {supabase_token}"}
    )
    
    assert response.status_code == 200
    user_data = response.json()
    assert "id" in user_data
    assert "email" in user_data

def test_auth_endpoint_invalid_token():
    """Test that the auth endpoint rejects invalid tokens"""
    response = requests.get(
        f"{API_URL}/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401

def test_llm_endpoint_with_auth(supabase_token, llm_api_key):
    """Test that the LLM endpoint accepts requests with valid auth"""
    response = requests.post(
        f"{API_URL}/llm/generate",
        headers={"Authorization": f"Bearer {supabase_token}"},
        json={
            "provider": "gemini", 
            "model": "gemini-2.0-flash-001", 
            "messages": [{"role": "user", "content": "Hello"}],
            "api_key": llm_api_key,
            "temperature": 0.7,
            "max_tokens": 100
        }
    )
    
    assert response.status_code == 200

def test_llm_endpoint_without_auth():
    """Test that the LLM endpoint rejects requests without auth"""
    response = requests.post(
        f"{API_URL}/llm/generate",
        json={
            "provider": "anthropic", 
            "model": "claude-3-5-haiku-20241022", 
            "messages": [{"role": "user", "content": "Hello"}],
            "api_key": "dummy_key"
        }
    )
    
    assert response.status_code == 401