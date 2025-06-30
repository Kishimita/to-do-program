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


# initializing the fastAPI app 
app = FastAPI()

#create a class for the task model
class Task(BaseModel):
    user_id: int
    group: str
    description: str
    completed: bool = False


#create a empty list for items to add as tasks
tasks = []

@app.post("/tasks")
def add_task(task: str):
    tasks.append(task)
    return tasks

@app.get("/tasks", response_model=list[Task])
def list_tasks(limit: int = 10):
    return tasks[0:limit]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id : int) -> str:
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail=f"Task: {task_id} not found.")
    else:
        task = tasks[task_id]
    return task


