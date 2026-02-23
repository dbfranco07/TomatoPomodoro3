import json
import uuid
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
STATIC_DIR = SRC_DIR / "static"
ASSETS_DIR = BASE_DIR / "assets"
TASKS_FILE = SRC_DIR / "tasks.json"


def load_tasks() -> List[dict]:
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]")
    return json.loads(TASKS_FILE.read_text())


def save_tasks(tasks: List[dict]) -> None:
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


app = FastAPI(title="TomatoPomodoro")

app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


# --- Task models ---

class TaskCreate(BaseModel):
    text: str


class TaskUpdate(BaseModel):
    checked: bool


class TaskReorder(BaseModel):
    ids: List[str]


# --- Task endpoints ---

@app.get("/tasks")
def get_tasks():
    return load_tasks()


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    tasks = load_tasks()
    task = {"id": str(uuid.uuid4()), "text": body.text.strip(), "checked": False}
    tasks.append(task)
    save_tasks(tasks)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: str, body: TaskUpdate):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["checked"] = body.checked
            save_tasks(tasks)
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks/reorder")
def reorder_tasks(body: TaskReorder):
    tasks = load_tasks()
    task_map = {t["id"]: t for t in tasks}
    reordered = []
    for tid in body.ids:
        if tid in task_map:
            reordered.append(task_map[tid])
    # Append any tasks not included in the ids list (safety net)
    included = set(body.ids)
    for t in tasks:
        if t["id"] not in included:
            reordered.append(t)
    save_tasks(reordered)
    return reordered


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    save_tasks(new_tasks)
