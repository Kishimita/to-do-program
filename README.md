# To-Do Program with FastAPI & React

Welcome to a simple to-do program. The purpose of this project is to learn about full-stack web development using a modern Python and JavaScript stack.

## Tech Stack

*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Database:** [SQLite](https://www.sqlite.org/index.html) for persistent data storage.
*   **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) for data modeling and database interaction.
*   **Frontend:** [React](https://react.dev/) with [Vite](https://vitejs.dev/) for a fast and modern UI.

## Setup and Running the Project

### 1. Backend Setup (FastAPI)

First, set up and run the Python backend.

```bash
# From the project root directory (to-do-program)

# Create and activate a Python virtual environment
# On macOS/Linux:
python3 -m venv .to-do-venv
source .to-do-venv/bin/activate

# Install Python dependencies
# (You should create a requirements.txt file first by running: pip freeze > requirements.txt)
pip install -r requirements.txt

# Run the backend server
uvicorn todo:app --reload
```
The backend will be running at `http://127.0.0.1:8000`. The first time you run it, it will create a `tasks.db` file.

### 2. Frontend Setup (React)

In a separate terminal, set up and run the React frontend.

```bash
# Navigate to the frontend directory
cd frontend-vite

# Install Node.js dependencies
npm install

# Run the frontend development server
npm run dev
```
You can now access the application in your browser at the address provided by Vite (usually `http://localhost:5173`).