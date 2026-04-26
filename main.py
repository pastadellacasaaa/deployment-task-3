from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# in-memory "database"
tasks = []

class Task(BaseModel):
    title: str

@app.get("/")
def home():
    return {"message": "Task Tracker API is running"}

@app.post("/tasks")
def add_task(task: Task):
    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.get("/tasks")
def get_tasks():
    return tasks

@app.put("/tasks/{task_id}")
def mark_done(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return task
    return {"error": "Task not found"}