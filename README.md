# ShuScribe

AI tool for creating narrative wikis.

## Dev Set Up

### Backend

<!-- #### Running the Backend (and Database)

  ```bash
  # Start containers in foreground (see logs directly)
  docker-compose up

  # Rebuild containers and start (use after dependency changes)
  docker-compose up --build
  
  # Start containers in background (detached mode)
  docker-compose up -d
  ```

- The FastAPI server will be running on `http://localhost:8000`
- The database will be running on `http://localhost:5432`
- The database adminer will be running on `http://localhost:5050` -->

#### Running the database

To just run the database:

  ```bash
  docker-compose up postgres # pgadmin
  ```

<!-- To update the database:

  ```bash
  ./db_migrate.sh "migration message"
  ``` -->

#### Running fastapi without docker (local development)

1. [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)


2. Navigate to the backend directory
  
    ```bash
    cd backend/shuscribe
    ```

3. Make sure all dependencies are installed

    ```bash
    uv sync
    ```

4. Run portkey gateway

    ```bash
    docker run --rm  -p 8787:8787 portkeyai/gateway:latest
    ```

5. Run the FastAPI server

    ```bash
    uvicorn main:app --reload
    ```

    ```bash
    uv run uvicorn main:app --reload
    ```

### Frontend

1. !!TODO