from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client.tasktracker
tasks_collection = db.tasks

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Task(BaseModel):
    title: str


# -------------------
# HOME PAGE
# -------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    tasks = list(tasks_collection.find({}, {"_id": 0}))

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "tasks": tasks
        }
    )


# -------------------
# ADD TASK FROM HTML FORM
# -------------------
@app.post("/add-task")
def add_task_from_form(title: str = Form(...)):
    last_task = tasks_collection.find_one(sort=[("id", -1)])
    new_id = 1 if last_task is None else last_task["id"] + 1

    new_task = {
        "id": new_id,
        "title": title,
        "done": False
    }

    tasks_collection.insert_one(new_task)

    return RedirectResponse(url="/", status_code=303)


# -------------------
# MARK TASK AS DONE FROM HTML
# -------------------
@app.get("/done/{task_id}")
def mark_done_from_html(task_id: int):
    tasks_collection.update_one(
        {"id": task_id},
        {"$set": {"done": True}}
    )

    return RedirectResponse(url="/", status_code=303)


# -------------------
# API HEALTH CHECK
# -------------------
@app.get("/api")
def api_home():
    return {
        "status": "success",
        "message": "Task Tracker API with MongoDB"
    }


# -------------------
# API CREATE TASK
# -------------------
@app.post("/tasks")
def add_task(task: Task):
    last_task = tasks_collection.find_one(sort=[("id", -1)])
    new_id = 1 if last_task is None else last_task["id"] + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks_collection.insert_one(new_task)
    new_task.pop("_id", None)

    return {
        "status": "success",
        "message": "Task created successfully",
        "task": new_task
    }


# -------------------
# API GET ALL TASKS
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
# API MARK TASK AS DONE
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