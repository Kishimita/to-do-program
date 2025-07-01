"""
To-do Program 

Functionality:
1. Add a task
2. View all tasks
3. Mark a task as completed
4. Remove a task
5. Save tasks to a sqlite database
6. Load tasks from a sqlite database
7. Exit the program

Date Created: 2025-06-10

Author: Kishimita
Tools Used:
- Python 3.12
- VS Code
- FASTAPI 
- UVicorn
- SQLModel
- SQLite
- TablePlus
- Github for version control
"""
 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict

# Define the Task model using SQLModel for database storage
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    group: str
    description: str
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

# SQLite database setup
sqlite_file_name = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Initialize FastAPI app
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- CRUD Endpoints using the database ---

@app.post("/tasks", response_model=Task)
def add_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.get("/tasks", response_model=List[Task])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    group: Optional[str] = None,
    completed: Optional[bool] = None
):
    with Session(engine) as session:
        query = select(Task).where(Task.deleted_at == None)
        if group is not None:
            query = query.where(Task.group == group)
        if completed is not None:
            query = query.where(Task.completed == completed)
        tasks = session.exec(query.offset(skip).limit(limit)).all()
        return tasks

@app.get("/tasks/user/{user_id}", response_model=List[Task])
def get_tasks_by_user(user_id: int):
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == user_id, Task.deleted_at == None)).all()
        return tasks

@app.get("/tasks/grouped", response_model=Dict[int, List[Task]])
def group_tasks_by_user():
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.deleted_at == None)).all()
        grouped = defaultdict(list)
        for task in tasks:
            grouped[task.user_id].append(task)
        return grouped

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        
        task_data = updated_task.model_dump(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task, key, value)

        # Set completed_at timestamp if task is being marked as complete
        if task.completed and not task.completed_at:
            task.completed_at = datetime.now()
        # If task is marked as not complete, clear the completed_at timestamp
        elif not task.completed:
            task.completed_at = None
        
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        
        # Soft delete by setting the deleted_at timestamp
        task.deleted_at = datetime.now()
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {"message": f"Task {task_id} marked as deleted."}

"""To-do 

-add a functionality to delete task in the ui/frontend , done
-add a datetime trait for each tast for tracking. done 
-add functionality for storing completed and never completed tasks in a sqlite db, done

"""