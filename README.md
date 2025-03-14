# ShuScribe

AI-assisted wiki-tool

## Dev Set Up

### Backend

#### Running the Backend (and Database)

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
<!-- - The database adminer will be running on `http://localhost:5050` -->

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

1. [Poetry Installation Guide](https://python-poetry.org/docs/#installing-with-pipx)

2. (Optional) Make sure that poetry creates a virtual environment in the backend directory to easily find it

    ```bash
    poetry config virtualenvs.in-project true
    ```

3. Navigate to the backend directory
  
    ```bash
    cd backend
    ```

4. Install all dependencies including development ones

    ```bash
    poetry install --with dev
    ```

5. Activate the virtual environment

    ```bash
    eval $(poetry env activate)
    ```

6. Run the FastAPI server

    ```bash
    uvicorn shuscribe.main:app --reload
    ```

7. Gracefully exit the virtual environment

    ```bash
    deactivate
    ```

### Frontend

1. !!TODO

