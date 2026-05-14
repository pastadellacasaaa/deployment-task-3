from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client.tasktracker
tasks_collection = db.tasks

app = FastAPI()


class Task(BaseModel):
    title: str


# -------------------
# HEALTH CHECK
# -------------------
@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Task Tracker API with MongoDB"
    }


# -------------------
# CREATE TASK
# -------------------
@app.post("/tasks")
def add_task(task: Task):
    # Generate a simple numeric ID
    last_task = tasks_collection.find_one(sort=[("id", -1)])
    new_id = 1 if last_task is None else last_task["id"] + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks_collection.insert_one(new_task)

    # Remove MongoDB's internal _id before returning response
    new_task.pop("_id", None)

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
    tasks = list(tasks_collection.find({}, {"_id": 0}))

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
    result = tasks_collection.update_one(
        {"id": task_id},
        {"$set": {"done": True}}
    )

    if result.matched_count == 0:
        return {
            "status": "error",
            "message": "Task not found"
        }

    updated_task = tasks_collection.find_one(
        {"id": task_id},
        {"_id": 0}
    )

    return {
        "status": "success",
        "message": "Task marked as completed",
        "task": updated_task
    }