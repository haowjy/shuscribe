# backend/notebooks/README.md

# ShuScribe Backend Notebooks

This directory contains Jupyter notebooks (`.ipynb` files) for interactive development, testing, and debugging of the ShuScribe backend, particularly focused on the LLM processing pipeline (`src/services/llm/`).

## 🎯 Purpose

These notebooks are used for:

-   **Iterative Prompt Engineering**: Quickly test and refine LLM prompts.
-   **Pipeline Component Testing**: Debug individual steps of the wiki generation or entity extraction pipelines.
-   **Data Exploration**: Understand how raw story content is processed.
-   **Experimentation**: Try out new LLM models or techniques.
-   **Executable Documentation**: Illustrate how certain backend services are intended to be used.

## 🚀 Getting Started

To run these notebooks, ensure you have set up your `backend` environment and installed development dependencies, including `jupyterlab`.

1.  **Navigate to the backend directory:**
    ```bash
    cd shuscribe/backend
    ```

2.  **Ensure all dependencies are installed, including `jupyterlab`:**
    ```bash
    uv sync
    ```

3.  **Start Jupyter Lab:**
    ```bash
    uv run jupyter lab
    ```
    This will typically open a new tab in your web browser with the Jupyter Lab interface.

4.  **Open or create a notebook:**
    Navigate to the `notebooks/` directory within Jupyter Lab and open an existing `.ipynb` file or create a new one.

### Using Notebooks in VS Code

VS Code has excellent built-in support for Jupyter notebooks:

1.  **Open your `shuscribe` monorepo as a Multi-Root Workspace.**
2.  **Ensure the Python extension is installed.**
3.  **Select the correct Python interpreter:**
    *   Open any `.ipynb` file in this `notebooks/` directory.
    *   In the top-right corner (or via the Command Palette: `Python: Select Interpreter`), ensure the kernel selected is from your `backend/.venv` virtual environment. This allows your notebooks to correctly import and use modules from `src/`.

## ⚠️ Important Considerations

-   **Sensitive Information**: Be extremely cautious with raw API keys or sensitive data within notebooks. While `LLMService` handles decryption in memory, avoid hardcoding keys. Use environment variables if necessary, but ideally pass them dynamically from `config.py` (which reads from `.env`).
-   **Environment**: Always run notebooks within the `backend/.venv` to ensure all necessary project dependencies are available.
-   **Version Control**:
    -   **Commit "finished" notebooks**: If a notebook serves as clear documentation for a feature or a complex process, commit it (without sensitive output, if possible).
    -   **Avoid committing purely scratchpad notebooks**: For quick, throwaway tests, either don't save them or use a `.gitignore` entry if they contain volatile output (e.g., large data prints, API responses).
    -   **Clear outputs before committing**: It's good practice to clear all cell outputs (`Cell > All Output > Clear` in Jupyter Lab) before committing `.ipynb` files to avoid unnecessary diffs and reduce repository size.