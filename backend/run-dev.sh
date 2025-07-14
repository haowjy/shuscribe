#!/bin/bash
# Development server runner that always uses fresh environment

# Source the .env file to load fresh values
source .env

# Run the development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000