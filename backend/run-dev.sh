#!/bin/bash
# Development server runner that always uses fresh environment

# Source the .env file to load fresh values
source .env

# Run the development server with hypercorn (matches production)
# Note: hypercorn supports --reload for development hot-reloading
uv run hypercorn src.main:app --reload --bind [::]:8000