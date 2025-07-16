"""
Tests for Health Check and Root API endpoints
"""

import pytest
import time
from fastapi.testclient import TestClient

from src.main import app
from src.database.factory import init_repositories, reset_repositories


class TestHealthCheckEndpoint:
    """Test health check endpoint functionality"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_health_check_success(self, client: TestClient):
        """Test basic health check functionality"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields are present
        assert "status" in data
        assert "environment" in data
        assert "version" in data
        
        # Verify field values
        assert data["status"] == "healthy"
        assert isinstance(data["environment"], str)
        assert isinstance(data["version"], str)
        assert data["version"] == "0.1.0"
    
    def test_health_check_response_structure(self, client: TestClient):
        """Test health check response structure"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response has exactly the expected fields
        expected_fields = {"status", "environment", "version"}
        actual_fields = set(data.keys())
        assert actual_fields == expected_fields
        
        # Verify field types
        assert isinstance(data["status"], str)
        assert isinstance(data["environment"], str)
        assert isinstance(data["version"], str)
    
    def test_health_check_response_time(self, client: TestClient):
        """Test health check response time is reasonable"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Health check should respond within 1 second
        assert response_time < 1.0
    
    def test_health_check_multiple_requests(self, client: TestClient):
        """Test health check handles multiple consecutive requests"""
        responses = []
        
        # Make multiple requests in quick succession
        for _ in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    def test_health_check_http_methods(self, client: TestClient):
        """Test health check endpoint only accepts GET requests"""
        # GET should work
        get_response = client.get("/health")
        assert get_response.status_code == 200
        
        # Other methods should not be allowed
        post_response = client.post("/health")
        assert post_response.status_code == 405  # Method Not Allowed
        
        put_response = client.put("/health")
        assert put_response.status_code == 405
        
        delete_response = client.delete("/health")
        assert delete_response.status_code == 405
    
    def test_health_check_content_type(self, client: TestClient):
        """Test health check returns JSON content type"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")


class TestRootEndpoint:
    """Test root API endpoint functionality"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_root_endpoint_success(self, client: TestClient):
        """Test basic root endpoint functionality"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields are present
        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert "docs" in data
        
        # Verify field values
        assert data["message"] == "ShuScribe API"
        assert data["version"] == "0.1.0"
        assert isinstance(data["environment"], str)
        assert data["docs"] in ["/docs", "disabled"]
    
    def test_root_endpoint_response_structure(self, client: TestClient):
        """Test root endpoint response structure"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response has exactly the expected fields
        expected_fields = {"message", "version", "environment", "docs"}
        actual_fields = set(data.keys())
        assert actual_fields == expected_fields
        
        # Verify field types
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["environment"], str)
        assert isinstance(data["docs"], str)
    
    def test_root_endpoint_message_content(self, client: TestClient):
        """Test root endpoint message content is informative"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Message should identify the API
        assert "ShuScribe" in data["message"]
        assert "API" in data["message"]
        
        # Version should be semantic version format
        version = data["version"]
        version_parts = version.split(".")
        assert len(version_parts) == 3  # Major.Minor.Patch
        
        # Each part should be numeric
        for part in version_parts:
            assert part.isdigit()
    
    def test_root_endpoint_docs_configuration(self, client: TestClient):
        """Test root endpoint docs field reflects configuration"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        docs_value = data["docs"]
        
        # Should be either the docs path or disabled
        assert docs_value in ["/docs", "disabled"]
        
        # If docs are enabled, verify the endpoint exists
        if docs_value == "/docs":
            docs_response = client.get("/docs")
            # Should either succeed or redirect, but not 404
            assert docs_response.status_code in [200, 307, 308]
    
    def test_root_endpoint_response_time(self, client: TestClient):
        """Test root endpoint response time is reasonable"""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Root endpoint should respond within 1 second
        assert response_time < 1.0
    
    def test_root_endpoint_http_methods(self, client: TestClient):
        """Test root endpoint only accepts GET requests"""
        # GET should work
        get_response = client.get("/")
        assert get_response.status_code == 200
        
        # Other methods should not be allowed
        post_response = client.post("/")
        assert post_response.status_code == 405  # Method Not Allowed
        
        put_response = client.put("/")
        assert put_response.status_code == 405
        
        delete_response = client.delete("/")
        assert delete_response.status_code == 405


class TestAPIEndpointsSecurity:
    """Test security aspects of health and root endpoints"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_health_endpoint_no_sensitive_info(self, client: TestClient):
        """Test health endpoint doesn't expose sensitive information"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Convert response to string for searching
        response_text = str(data).lower()
        
        # Should not contain sensitive information
        sensitive_terms = [
            "password", "secret", "key", "token", "database",
            "connection", "host", "port", "username", "admin"
        ]
        
        for term in sensitive_terms:
            assert term not in response_text, f"Sensitive term '{term}' found in health check response"
    
    def test_root_endpoint_no_sensitive_info(self, client: TestClient):
        """Test root endpoint doesn't expose sensitive information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Convert response to string for searching
        response_text = str(data).lower()
        
        # Should not contain sensitive information
        sensitive_terms = [
            "password", "secret", "key", "token", "database",
            "connection", "host", "port", "username", "admin"
        ]
        
        for term in sensitive_terms:
            assert term not in response_text, f"Sensitive term '{term}' found in root endpoint response"
    
    def test_endpoints_cors_headers(self, client: TestClient):
        """Test that endpoints respect CORS configuration"""
        # Test health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Test root endpoint
        root_response = client.get("/")
        assert root_response.status_code == 200
        
        # CORS headers should be present if configured
        # (Note: Actual CORS testing would require preflight requests)
        # For now, just verify the endpoints work without CORS errors
    
    def test_endpoints_rate_limiting_resilience(self, client: TestClient):
        """Test endpoints handle rapid requests gracefully"""
        # Make many rapid requests to both endpoints
        health_responses = []
        root_responses = []
        
        for _ in range(20):
            health_responses.append(client.get("/health"))
            root_responses.append(client.get("/"))
        
        # All requests should succeed (no rate limiting implemented)
        for response in health_responses:
            assert response.status_code == 200
        
        for response in root_responses:
            assert response.status_code == 200


class TestAPIEndpointsIntegration:
    """Test integration scenarios for health and root endpoints"""
    
    @pytest.fixture(autouse=True)
    async def setup_repositories(self):
        """Set up memory repositories for each test"""
        reset_repositories()
        init_repositories(backend="memory")
        yield
        reset_repositories()
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_endpoints_consistency(self, client: TestClient):
        """Test that both endpoints return consistent version and environment"""
        health_response = client.get("/health")
        root_response = client.get("/")
        
        assert health_response.status_code == 200
        assert root_response.status_code == 200
        
        health_data = health_response.json()
        root_data = root_response.json()
        
        # Version should be consistent between endpoints
        assert health_data["version"] == root_data["version"]
        
        # Environment should be consistent between endpoints
        assert health_data["environment"] == root_data["environment"]
    
    async def test_endpoints_after_repository_operations(self, client: TestClient):
        """Test endpoints still work after repository operations"""
        # Perform some repository operations first
        from src.database.factory import get_repositories
        
        repos = get_repositories()
        
        # Create a test project
        project_data = {
            "id": "health-test-project",
            "title": "Health Test Project"
        }
        project = await repos.project.create(project_data)
        
        # Now test the health endpoints
        health_response = client.get("/health")
        root_response = client.get("/")
        
        assert health_response.status_code == 200
        assert root_response.status_code == 200
        
        # Health status should still be healthy
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        # Root endpoint should still work normally
        root_data = root_response.json()
        assert root_data["message"] == "ShuScribe API"
        
        # Clean up
        await repos.project.delete(project.id)
    
    def test_endpoints_concurrent_access(self, client: TestClient):
        """Test endpoints work correctly under concurrent access simulation"""
        import concurrent.futures
        
        def make_health_request():
            return client.get("/health")
        
        def make_root_request():
            return client.get("/")
        
        # Simulate concurrent access
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit multiple concurrent requests
            health_futures = [executor.submit(make_health_request) for _ in range(10)]
            root_futures = [executor.submit(make_root_request) for _ in range(10)]
            
            # Wait for all to complete
            health_responses = [future.result() for future in health_futures]
            root_responses = [future.result() for future in root_futures]
        
        # All should succeed
        for response in health_responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        
        for response in root_responses:
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "ShuScribe API"