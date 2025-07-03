# LLM Service Integration Tests

This directory contains integration tests for the LLM Service that require external dependencies and API keys.

## Prerequisites

### 1. Portkey Gateway

The tests require a running Portkey Gateway instance:

```bash
# Start the Portkey Gateway
docker run -d \
  --name portkey-gateway \
  -p 8787:8787 \
  portkeyai/gateway:latest

# Verify it's running
curl http://localhost:8787/
```

### 2. API Keys

You need valid API keys for the LLM providers you want to test. Add them to your `.env` file in the backend directory:

```env
# Required for integration tests
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Portkey configuration
PORTKEY_BASE_URL=http://localhost:8787/v1
```

### 3. Python Environment

Make sure you have the development dependencies installed:

```bash
# From the backend directory
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running the Tests

### Run All Integration Tests

```bash
# From the backend directory
pytest -m integration tests/test_services/test_llm/
```

### Run Specific Test Classes

```bash
# Test basic LLM service functionality
pytest -m integration tests/test_services/test_llm/test_llm_service_integration.py::TestLLMServiceIntegration

# Test performance aspects
pytest -m integration tests/test_services/test_llm/test_llm_service_integration.py::TestLLMServicePerformance
```

### Run Tests for Specific Providers

```bash
# Test only OpenAI
pytest -m integration tests/test_services/test_llm/test_llm_service_integration.py::TestLLMServiceIntegration::test_chat_completion_per_provider[openai]

# Test only Google
pytest -m integration tests/test_services/test_llm/test_llm_service_integration.py::TestLLMServiceIntegration::test_chat_completion_per_provider[google]

# Test only Anthropic
pytest -m integration tests/test_services/test_llm/test_llm_service_integration.py::TestLLMServiceIntegration::test_chat_completion_per_provider[anthropic]
```

### Verbose Output

```bash
# See detailed output including API responses
pytest -m integration -v -s tests/test_services/test_llm/
```

## Test Coverage

The integration tests cover:

- **Service Initialization**: Verifying the LLM service starts correctly
- **API Key Management**: Testing encrypted storage and retrieval of API keys
- **Chat Completion**: Testing non-streaming responses from all providers
- **Streaming**: Testing streaming responses and latency
- **Concurrent Requests**: Testing multiple providers simultaneously
- **Error Handling**: Testing invalid models and missing API keys
- **Performance**: Testing response times and streaming latency

## Skipped Tests

Tests will be automatically skipped if:

- The Portkey Gateway is not running
- Required API keys are missing from the `.env` file
- Specific provider API keys are not available for provider-specific tests

## Troubleshooting

### Portkey Gateway Issues

```bash
# Check if the gateway is running
docker ps | grep portkey-gateway

# Check gateway logs
docker logs portkey-gateway

# Restart the gateway
docker restart portkey-gateway
```

### API Key Issues

- Ensure your API keys are valid and have sufficient credits
- Check that the keys are properly set in your `.env` file
- Verify the key format matches the expected pattern for each provider

### Network Issues

- The tests require internet access to reach the LLM provider APIs
- If you're behind a corporate firewall, you may need to configure proxy settings
- Some providers may have rate limits that could cause tests to fail if run too frequently

## Integration with Regular Tests

These integration tests are marked with `@pytest.mark.integration` and are **excluded** from the regular test suite. This means:

- `pytest` or `pytest tests/` will **not** run these tests
- You must explicitly run `pytest -m integration` to execute them
- This keeps the regular test suite fast and doesn't require external dependencies

## CI/CD Considerations

For CI/CD pipelines, you may want to:

1. Run these tests in a separate job/stage
2. Use secrets management for API keys
3. Set up the Portkey Gateway as a service
4. Consider using test API keys or mock services for faster execution 