FROM python:3.12-slim

# TODO

# # Install uv.
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# # Copy the application into the container.
# COPY shuscribe /app

# # Install the application dependencies.
# WORKDIR /app
# RUN uv sync --frozen --no-cache

# # Run the application.
# CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]


# FROM python:3.12-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Install poetry
# RUN pip install --no-cache-dir poetry==2.0.1

# # Copy poetry configuration files
# COPY pyproject.toml poetry.lock ./

# # Configure poetry to not create a virtual environment
# RUN poetry config virtualenvs.create false

# # Install dependencies
# RUN poetry install --no-interaction --no-ansi --no-root

# # Copy the rest of the application
# COPY shuscribe ./shuscribe
# COPY alembic.ini ./
# COPY migrations ./migrations

# # Set environment variables
# ENV PYTHONPATH=/app
# ENV PYTHONUNBUFFERED=1

# # Expose port
# EXPOSE 8000

# # Run the application with uvicorn
# CMD ["uvicorn", "shuscribe.main:app", "--host", "0.0.0.0", "--port", "8000"]