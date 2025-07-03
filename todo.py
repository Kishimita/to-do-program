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
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict

# Define the Task model using SQLModel for database storage
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    category: str
    description: str
    completed: bool = Field(default=False)
    percent_complete: float = Field(default=0.0, ge=0, le=100) # new percent complete feature
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None) # new updated task feature 
    completed_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

# --- Pydantic Models for API data shapes ---

class TaskCreate(BaseModel):
    """Model for creating a new task. Only includes fields the user provides."""
    user_id: int
    category: str
    description: str
    completed: bool = False
    percent_complete: float = 0.0

class TaskUpdate(BaseModel):
    """Model for updating an existing task. Fields are optional."""
    category: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    percent_complete: Optional[float] = None


# SQLite database setup
sqlite_file_name = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

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
def add_task(task_data: TaskCreate): # FIX: Use TaskCreate to correctly receive data
    # If a task is created as 'completed', its percentage must be 100.
    if task_data.completed:
        task_data.percent_complete = 100.0
    
    # Create a full Task DB model from the provided data
    new_task = Task.model_validate(task_data)

    with Session(engine) as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task

@app.get("/tasks", response_model=List[Task])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    completed: Optional[bool] = None
):
    with Session(engine) as session:
        query = select(Task).where(Task.deleted_at == None)
        if category is not None:
            query = query.where(Task.category == category)
        if completed is not None:
            query = query.where(Task.completed == completed)
        tasks = session.exec(query.offset(skip).limit(limit)).all()
        return tasks
    
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        return task
    
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

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update_data: TaskUpdate): # Use the new TaskUpdate model
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.deleted_at is not None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        
        # Get the update data, excluding any fields that were not set
        update_data = task_update_data.model_dump(exclude_unset=True)
        
        # Update the model with the new data
        for key, value in update_data.items():
            setattr(task, key, value)

        # If task is marked as complete, force percentage to 100.
        if task.completed:
            task.percent_complete = 100.0
            if not task.completed_at:
                task.completed_at = datetime.now()
        # If task is marked as not complete, clear the completed_at timestamp.
        else:
            task.completed_at = None
        
        task.updated_at = datetime.now()
        
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

From a quick overview: 
[x] Fix Night mode in UI, doesnt appear to work 
[x] Fix Filter button, it does not work
[x] Allow user to mark task as completed with a toggle button, similar to the delete button
[x] Since you update tasks, an updated_at column would actually be extremely 
helpful to a user.
[] For a realistic setup, the delete_at stuff should be gone and the task should actually be deleted. (Pin on this)
[] It seems to me that group_task_by_user should make use of list_tasks 
instead.
[] Searching can go from simple key word search to 
something like rank search, semantic search, etc.
[] I would organize the code a bit more in the sense that all functions should be grouped and kept separate from code 
being executed in the script. As in, you’re running app commands but also declaring functions
so it’s a bit hard to read.
[] Focus on is sorting and searching. Sorting can go from basic stuff like by creation time to more complex 
like task subject (in an unsupervised manner), or priority if you add a way 
like this task should only be completed after this other task (it will 
form a graph).


Overall Advice : It depends on the balance between algorithms and AI that you want. But I do 
think showing off knowledge of AI, ML, Algorithms, and/or Data Structures 
will be helpful.
"""