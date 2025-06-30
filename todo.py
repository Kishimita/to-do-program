"""
To-do Program 

Functionality:
1. Add a task
2. View all tasks
3. Mark a task as completed
4. Remove a task
5. Save tasks to a file
6. Load tasks from a file
7. Exit the program

Date Created: 2025-06-10

Author: Kishimita
Tools Used:
- Python 3.12
- VS Code
- FASTAPI 
- UVicorn
- add the rest of the tools you used 
- Github for version control
"""
 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict

# initializing the fastAPI app 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#create a class for the task model
class Task(BaseModel):
    user_id: int
    group: str
    description: str
    completed: bool = False


#create a empty list for items to add as tasks
tasks = []

@app.post("/tasks", response_model=list[Task])
def add_task(task: Task):
    tasks.append(task)
    return tasks


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, user_id: int):
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail=f"Task: {task_id} not found.")
    if tasks[task_id].user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks.")
    tasks[task_id] = updated_task
    return updated_task

@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, user_id: int):
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail=f"Task: {task_id} not found.")
    if tasks[task_id].user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own tasks.")
    removed_task = tasks.pop(task_id)
    return {"message": f"Task {task_id} deleted.", "task": removed_task}

@app.get("/tasks", response_model=list[Task])
def list_tasks(
    skip: int = 0,
    limit: int = 10,
    group: str | None = None,
    completed: bool | None = None
):
    filtered_tasks = tasks
    if group is not None:
        filtered_tasks = [task for task in filtered_tasks if task.group == group]
    if completed is not None:
        filtered_tasks = [task for task in filtered_tasks if task.completed == completed]
    return filtered_tasks[skip:skip+limit]

@app.get("/tasks/user/{user_id}", response_model=list[Task])
def get_tasks_by_user(user_id: int):
    return [task for task in tasks if task.user_id == user_id]

@app.get("/tasks/grouped", response_model=dict)
def group_tasks_by_user():
    grouped = defaultdict(list)
    for task in tasks:
        grouped[task.user_id].append(task)
    return grouped

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id : int) -> str:
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail=f"Task: {task_id} not found.")
    else:
        task = tasks[task_id]
    return task


