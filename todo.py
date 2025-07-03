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
    percent_complete: float = Field(default=0.0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CRUD Endpoints using the database ---

@app.post("/tasks", response_model=Task)
def add_task(task_data: TaskCreate):
    if task_data.completed:
        task_data.percent_complete = 100.0
    
    new_task = Task.model_validate(task_data)

    with Session(engine) as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task

# This is the new, consolidated endpoint for getting tasks.
# It replaces both the old list_tasks and sort_tasks functions.
@app.get("/tasks", response_model=List[Task])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    completed: Optional[bool] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "asc"
):
    """
    A single, powerful endpoint to get tasks.
    Handles filtering by category and completion status, and sorting.
    """
    with Session(engine) as session:
        query = select(Task)

        # Filtering
        if category:
            # Use ilike for case-insensitive partial matching
            query = query.where(Task.category.ilike(f"%{category}%"))
        if completed is not None:
            query = query.where(Task.completed == completed)

        # Sorting
        # Use getattr to safely get the column for sorting, default to created_at
        sort_column = getattr(Task, sort_by, Task.created_at)
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Pagination
        query = query.offset(skip).limit(limit)
        
        tasks = session.exec(query).all()
        return tasks

# --- Old list_tasks function, now commented out and replaced by the new get_tasks ---
# @app.get("/tasks", response_model=List[Task])
# def list_tasks(
#     skip: int = 0,
#     limit: int = 100,
#     category: Optional[str] = None,
#     completed: Optional[bool] = None
# ):
#     with Session(engine) as session:
#         query = select(Task)
#         if category is not None:
#             query = query.where(Task.category == category)
#         if completed is not None:
#             query = query.where(Task.completed == completed)
#         tasks = session.exec(query.offset(skip).limit(limit)).all()
#         return tasks
    
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        return task
    
@app.get("/tasks/user/{user_id}", response_model=List[Task])
def get_tasks_by_user(user_id: int):
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        return tasks

@app.get("/tasks/grouped", response_model=Dict[int, List[Task]])
def group_tasks_by_user():
    # Refactored to reuse the new get_tasks logic
    all_tasks = get_tasks(limit=1000)
    grouped = defaultdict(list)
    for task in all_tasks:
        if task.user_id is not None:
            grouped[task.user_id].append(task)
    return grouped

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update_data: TaskUpdate):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found.")
        
        update_data = task_update_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(task, key, value)

        if task.completed:
            task.percent_complete = 100.0
            if not task.completed_at:
                task.completed_at = datetime.now()
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
        
        session.delete(task)
        session.commit()
        
        return {"message": f"Task {task_id} has been permanently deleted."}

# --- Old sort_tasks function, now commented out and replaced by the new get_tasks ---
# @app.get("/tasks/sorted", response_model=List[Task])
# def sort_tasks(
#     user_id: Optional[int] = None,
#     category: Optional[str] = None,
#     completed: Optional[bool] = None,
#     sort_by: Optional[str] = "created_at",
#     order: Optional[str] = "asc"
# ):
#     with Session(engine) as session:
#         query = select(Task)
#         if user_id is not None:
#             query = query.where(Task.user_id == user_id)
#         if category is not None:
#             query = query.where(Task.category == category)
#         if completed is not None:
#             query = query.where(Task.completed == completed)
#         if sort_by == "created_at":
#             query = query.order_by(Task.created_at.asc() if order == "asc" else Task.created_at.desc())
#         elif sort_by == "updated_at":
#             query = query.order_by(Task.updated_at.asc() if order == "asc" else Task.updated_at.desc())
#         tasks = session.exec(query).all()
#         return tasks

"""To-do 

From a quick overview: 
[x] Fix Night mode in UI, doesnt appear to work 
[x] Fix Filter button, it does not work
[x] Allow user to mark task as completed with a toggle button, similar to the delete button
[x] Since you update tasks, an updated_at column would actually be extremely 
helpful to a user.


[x] For a realistic setup, the delete_at stuff should be gone and the task should actually be deleted. (Pin on this)
[x] It seems to me that group_task_by_user should make use of list_tasks 
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