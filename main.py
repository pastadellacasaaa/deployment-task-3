from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# in-memory "database"
tasks = []

class Task(BaseModel):
    title: str


# -------------------
# HEALTH CHECK
# -------------------
@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Task Tracker API UPDATED v2"
    }


# -------------------
# CREATE TASK
# -------------------
@app.post("/tasks")
def add_task(task: Task):
    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }
    tasks.append(new_task)

    return {
        "status": "success",
        "message": "Task created successfully",
        "task": new_task
    }


# -------------------
# GET ALL TASKS
# -------------------
@app.get("/tasks")
def get_tasks():
    return {
        "status": "success",
        "count": len(tasks),
        "tasks": tasks
    }


# -------------------
# MARK TASK AS DONE
# -------------------
@app.put("/tasks/{task_id}")
def mark_done(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return {
                "status": "success",
                "message": "Task marked as completed",
                "task": task
            }

    return {
        "status": "error",
        "message": "Task not found"
    }