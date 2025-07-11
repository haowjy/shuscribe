# """
# Integration tests for LLM Service

# These tests require:
# 1. A running Portkey Gateway at http://localhost:8787
# 2. Valid API keys in environment variables (OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY)
# 3. External API access

# Run with: pytest -m integration tests/test_services/test_llm/test_llm_service_integration.py
# """

# import os
# import pytest
# import asyncio
# from typing import Dict, Any, List, cast, AsyncIterator
# from uuid import uuid4

# from src.config import settings
# from src.core.constants import PROVIDER_ID
# from src.services.llm.llm_service import LLMService
# from src.api.dependencies import get_user_repository_dependency
# from src.schemas.llm.models import LLMMessage, LLMResponse
# from src.schemas.db.user import UserCreate, UserAPIKeyCreate
# from src.core.encryption import encrypt_api_key
# from src.database.interfaces.user_repository import IUserRepository
# from dotenv import dotenv_values


# @pytest.fixture(scope="module")
# def portkey_gateway_check():
#     """Check if Portkey Gateway is running before tests."""
#     import httpx
    
#     try:
#         response = httpx.get("http://localhost:8787/", timeout=5.0)
#         if response.status_code != 200:
#             pytest.skip("Portkey Gateway not responding at http://localhost:8787")
#     except Exception:
#         pytest.skip("Portkey Gateway not running at http://localhost:8787 - start with: docker run -d --name portkey-gateway -p 8787:8787 portkeyai/gateway:latest")


# @pytest.fixture(scope="module")
# def api_keys_check():
#     """Check if required API keys are available."""
#     env_values = dotenv_values()
#     required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"]
    
#     missing_keys = []
#     for key in required_keys:
#         if not env_values.get(key):
#             missing_keys.append(key)
    
#     if missing_keys:
#         pytest.skip(f"Missing required API keys in .env: {', '.join(missing_keys)}")
    
#     return env_values


# @pytest.fixture
# async def llm_service():
#     """Create LLM service instance with in-memory repository."""
#     # Ensure we're using memory backend for integration tests
#     original_skip_db = os.environ.get("SKIP_DATABASE")
#     os.environ["SKIP_DATABASE"] = "true"
    
#     try:
#         service = LLMService(user_repository=get_user_repository_dependency())
#         # Ensure repository is properly initialized
#         assert service.user_repository is not None, "User repository should be initialized"
#         yield service
#     finally:
#         # Restore original setting
#         if original_skip_db is not None:
#             os.environ["SKIP_DATABASE"] = original_skip_db
#         else:
#             os.environ.pop("SKIP_DATABASE", None)


# @pytest.fixture
# async def test_user_with_api_keys(llm_service: LLMService, api_keys_check: Dict[str, str]):
#     """Create a test user with encrypted API keys stored."""
#     # Create test user
#     assert llm_service.user_repository is not None, "User repository should be initialized"
#     user = await llm_service.user_repository.create_user(UserCreate(
#         email=f"test-{uuid4().hex[:8]}@example.com",
#         display_name="LLM Test User"
#     ))
    
#     # Store API keys from environment
#     stored_providers = []
#     for provider in LLMService.get_all_llm_providers():
#         provider_id = provider.provider_id
#         api_key = api_keys_check.get(f"{provider_id.upper()}_API_KEY")
        
#         if api_key:
#             # Encrypt and store the API key
#             encrypted_key = encrypt_api_key(api_key)
#             await llm_service.user_repository.store_api_key(
#                 user_id=user.id,
#                 api_key_data=UserAPIKeyCreate(
#                     provider=provider_id,
#                     api_key=api_key,
#                     provider_metadata={}
#                 ),
#                 encrypted_key=encrypted_key
#             )
#             stored_providers.append(provider_id)
    
#     return {
#         "user": user,
#         "stored_providers": stored_providers
#     }


# @pytest.mark.integration
# class TestLLMServiceIntegration:
#     """Integration tests for LLM Service with real API providers."""
    
#     async def test_service_initialization(self, llm_service: LLMService, portkey_gateway_check):
#         """Test that LLM service initializes correctly."""
#         assert llm_service.user_repository is not None
#         assert settings.PORTKEY_BASE_URL == "http://localhost:8787/v1"
#         assert settings.DATABASE_BACKEND == "memory"
    
#     async def test_api_key_storage_and_retrieval(self, llm_service: LLMService, test_user_with_api_keys: Dict[str, Any]):
#         """Test that API keys are properly stored and can be retrieved."""
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         # Verify API keys were stored
#         assert llm_service.user_repository is not None, "User repository should be initialized"
#         stored_keys = await llm_service.user_repository.get_user_api_keys(user.id)
#         assert len(stored_keys) == len(stored_providers)
        
#         # Verify each provider is available
#         for provider_id in stored_providers:
#             provider_keys = [k for k in stored_keys if k.provider == provider_id]
#             assert len(provider_keys) == 1
#             assert provider_keys[0].provider == provider_id
    
#     @pytest.mark.parametrize("provider_id", ["openai", "google", "anthropic"])
#     async def test_chat_completion_per_provider(
#         self, 
#         llm_service: LLMService, 
#         test_user_with_api_keys: Dict[str, Any],
#         provider_id: PROVIDER_ID,
#         portkey_gateway_check
#     ):
#         """Test chat completion for each provider individually."""
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         if provider_id not in stored_providers:
#             pytest.skip(f"No API key available for {provider_id}")
        
#         # Get default test model for this provider
#         test_model = LLMService.get_default_test_model_name_for_provider(provider_id)
#         assert test_model is not None, f"No default test model for {provider_id}"
        
#         # Make a simple chat completion call
#         response = await llm_service.chat_completion(
#             provider=provider_id,
#             model=test_model,
#             messages=[LLMMessage(role="user", content="Hello")],
#             user_id=user.id,
#             max_tokens=10,
#             temperature=0.0,
#             stream=False
#         )
        
#         response = cast(LLMResponse, response)
#         assert response.content is not None
#         assert len(response.content.strip()) > 0
#         assert response.model is not None
#         assert response.usage is not None
#         assert response.usage.get("prompt_tokens", 0) > 0
#         assert response.usage.get("completion_tokens", 0) > 0
        
#         # Show the response
#         print(f"\n🤖 {provider_id.upper()} Response:")
#         print(f"   Model: {response.model}")
#         print(f"   Content: '{response.content.strip()}'")
#         print(f"   Tokens: {response.usage.get('prompt_tokens', 0)} prompt + {response.usage.get('completion_tokens', 0)} completion")
    
#     async def test_streaming_chat_completion(
#         self, 
#         llm_service: LLMService, 
#         test_user_with_api_keys: Dict[str, Any],
#         portkey_gateway_check
#     ):
#         """Test streaming chat completion functionality."""
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         # Use Google as default for streaming test (fast and reliable)
#         test_provider = "google"
#         if test_provider not in stored_providers:
#             pytest.skip(f"No API key available for {test_provider}")
        
#         test_model = LLMService.get_default_test_model_name_for_provider(test_provider)
#         assert test_model is not None
        
#         # Make a streaming chat completion call
#         response_stream = await llm_service.chat_completion(
#             provider=test_provider,
#             model=test_model,
#             messages=[LLMMessage(role="user", content="Write a very short story about a robot.")],
#             user_id=user.id,
#             max_tokens=50,
#             temperature=0.7,
#             stream=True
#         )
        
#         response_stream = cast(AsyncIterator[LLMResponse], response_stream)
        
#         # Collect all chunks and show streaming output
#         chunks = []
#         full_content = ""
#         print(f"\n🎬 Streaming Response from {test_provider}:")
#         print("   📡 ", end="", flush=True)
#         async for chunk in response_stream:
#             chunks.append(chunk)
#             full_content += chunk.content
#             print(chunk.content, end="", flush=True)
#         print(f"\n   ✅ Received {len(chunks)} chunks, total length: {len(full_content)} chars")
        
#         # Verify streaming response
#         assert len(chunks) > 1, "Should receive multiple chunks"
#         assert len(full_content.strip()) > 0, "Should have content"
        
#         # Verify each chunk is a valid LLMResponse
#         for chunk in chunks:
#             assert isinstance(chunk, LLMResponse)
#             assert chunk.content is not None
    
#     async def test_multiple_providers_concurrent(
#         self, 
#         llm_service: LLMService, 
#         test_user_with_api_keys: Dict[str, Any],
#         portkey_gateway_check
#     ):
#         """Test making concurrent requests to multiple providers."""
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         # Create tasks for each available provider
#         tasks = []
#         for provider_id in stored_providers:
#             test_model = LLMService.get_default_test_model_name_for_provider(provider_id)
#             if test_model:
#                 task = llm_service.chat_completion(
#                     provider=provider_id,
#                     model=test_model,
#                     messages=[LLMMessage(role="user", content=f"Say hello from {provider_id}")],
#                     user_id=user.id,
#                     max_tokens=15,
#                     temperature=0.0,
#                     stream=False
#                 )
#                 tasks.append((provider_id, task))
        
#         # Execute all tasks concurrently
#         results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
#         # Verify all requests succeeded
#         successful_responses = 0
#         for i, (provider_id, result) in enumerate(zip([p for p, _ in tasks], results)):
#             if isinstance(result, Exception):
#                 pytest.fail(f"Request to {provider_id} failed: {result}")
#             else:
#                 response = cast(LLMResponse, result)
#                 assert response.content is not None
#                 assert len(response.content.strip()) > 0
#                 successful_responses += 1
        
#         assert successful_responses == len(tasks), "All concurrent requests should succeed"
    
#     async def test_error_handling_invalid_model(
#         self, 
#         llm_service: LLMService, 
#         test_user_with_api_keys: Dict[str, Any],
#         portkey_gateway_check
#     ):
#         """Test error handling for invalid model names."""
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         if not stored_providers:
#             pytest.skip("No API keys available for testing")
        
#         # Use first available provider with invalid model
#         test_provider = stored_providers[0]
#         invalid_model = "definitely-not-a-real-model-name"
        
#         # Should raise an exception for invalid model
#         with pytest.raises(Exception) as exc_info:
#             await llm_service.chat_completion(
#                 provider=test_provider,
#                 model=invalid_model, # type: ignore
#                 messages=[LLMMessage(role="user", content="Hello")],
#                 user_id=user.id,
#                 max_tokens=10,
#                 temperature=0.0,
#                 stream=False
#             )
        
#         # Verify it's a meaningful error
#         assert "model" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
    
#     async def test_error_handling_missing_api_key(
#         self, 
#         llm_service: LLMService,
#         portkey_gateway_check
#     ):
#         """Test error handling when user has no API key for requested provider."""
#         # Create user without API keys
#         assert llm_service.user_repository is not None, "User repository should be initialized"
#         user = await llm_service.user_repository.create_user(UserCreate(
#             email=f"no-keys-{uuid4().hex[:8]}@example.com",
#             display_name="No Keys User"
#         ))
        
#         # Try to use OpenAI without stored API key
#         with pytest.raises(Exception) as exc_info:
#             await llm_service.chat_completion(
#                 provider="openai",
#                 model="gpt-4.1-nano",
#                 messages=[LLMMessage(role="user", content="Hello")],
#                 user_id=user.id,
#                 max_tokens=10,
#                 temperature=0.0,
#                 stream=False
#             )
        
#         # Should get an error about missing API key
#         error_msg = str(exc_info.value).lower()
#         assert "api key" in error_msg or "key" in error_msg or "authentication" in error_msg


# @pytest.mark.integration
# class TestLLMServicePerformance:
#     """Performance-related integration tests."""
    
#     async def test_response_time_reasonable(
#         self, 
#         llm_service: LLMService, 
#         test_user_with_api_keys: Dict[str, Any],
#         portkey_gateway_check
#     ):
#         """Test that response times are reasonable for small requests."""
#         import time
        
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         if not stored_providers:
#             pytest.skip("No API keys available for performance testing")
        
#         # Test with fastest provider (usually Google)
#         test_provider = "google" if "google" in stored_providers else stored_providers[0]
#         test_model = LLMService.get_default_test_model_name_for_provider(test_provider)
        
#         start_time = time.time()
#         response = await llm_service.chat_completion(
#             provider=test_provider,
#             model=test_model,
#             messages=[LLMMessage(role="user", content="Hi")],
#             user_id=user.id,
#             max_tokens=5,
#             temperature=0.0,
#             stream=False
#         )
#         end_time = time.time()
        
#         response = cast(LLMResponse, response)
#         assert response.content is not None
        
#         # Response should be under 10 seconds for a simple request
#         response_time = end_time - start_time
#         assert response_time < 10.0, f"Response took {response_time:.2f}s, expected < 10s"
    
#     async def test_streaming_latency(
#         self, 
#         llm_service: LLMService, 
#         test_user_with_api_keys: Dict[str, Any],
#         portkey_gateway_check
#     ):
#         """Test that streaming responses start quickly."""
#         import time
        
#         user = test_user_with_api_keys["user"]
#         stored_providers = test_user_with_api_keys["stored_providers"]
        
#         if "google" not in stored_providers:
#             pytest.skip("Google API key required for streaming latency test")
        
#         test_model = LLMService.get_default_test_model_name_for_provider("google")
        
#         start_time = time.time()
#         response_stream = await llm_service.chat_completion(
#             provider="google",
#             model=test_model,
#             messages=[LLMMessage(role="user", content="Count from 1 to 10")],
#             user_id=user.id,
#             max_tokens=30,
#             temperature=0.0,
#             stream=True
#         )
        
#         response_stream = cast(AsyncIterator[LLMResponse], response_stream)
        
#         # Time to first chunk
#         first_chunk = await response_stream.__anext__()
#         first_chunk_time = time.time()
        
#         assert first_chunk.content is not None
        
#         # First chunk should arrive within 5 seconds
#         time_to_first_chunk = first_chunk_time - start_time
#         assert time_to_first_chunk < 5.0, f"First chunk took {time_to_first_chunk:.2f}s, expected < 5s" 