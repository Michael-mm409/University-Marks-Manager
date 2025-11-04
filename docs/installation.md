# Installation Guide

## Prerequisites

- Python 3.11 or higher (recommended)
- Docker and Docker Compose (for containerized deployment)
- Git (for cloning the repository)

## Quick Start with Docker (Recommended)

1. Clone the repository

   ```sh
   git clone https://github.com/yourusername/university-marks-manager.git
   cd university-marks-manager
   ```

2. Start with Docker Compose
   ```sh
   docker-compose up --build
   ```
   The application will be available at http://localhost:18000

## Local Development Setup

1. Clone the repository (if not already done)

2. Create a virtual environment

   ```sh
   python -m venv venv
   ```

3. Activate the virtual environment

   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

4. Install dependencies

   ```sh
   pip install -r requirements.txt
   ```

5. Run the application
   ```sh
   uvicorn src.app.main:app --reload
   ```
   Or use the provided startup scripts:
   - On Unix/Linux/macOS: `./StartMarkManager.sh`
   - On Windows: `StartMarkManager.bat`

To exit the virtual environment: `deactivate`

## Troubleshooting

- Ensure you are using Python 3.11 or higher: `python --version`
- For Docker issues, ensure the Docker daemon is running and you have sufficient permissions
- If you encounter database connection errors, check your `DATABASE_URL` environment variable
- If testing instructions are required and no TESTING.md exists, refer to the repository's tests/ directory or add a TESTING.md with project-specific testing steps
- For framework or deployment questions, refer to FastAPI docs: https://fastapi.tiangolo.com/
- If you encounter missing module errors, confirm dependencies are installed in the active environment

- To exit the virtual environment, use `deactivate`.
- For development or testing instructions, see [Testing Guide](TESTING.md).
