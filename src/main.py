import json
import uuid
from pathlib import Path
from typing import List

import anthropic
import openai
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
STATIC_DIR = SRC_DIR / "static"
TASKS_FILE = SRC_DIR / "tasks.json"
NOTES_FILE = SRC_DIR / "notes.txt"


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
    task = {"id": str(uuid.uuid4()), 
            "text": body.text.strip(), 
            "checked": False}
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


# --- Notes model ---

class NotesBody(BaseModel):
    content: str


# --- Notes endpoints ---

@app.get("/notes")
def get_notes():
    content = NOTES_FILE.read_text(encoding="utf-8") if NOTES_FILE.exists() else ""
    return {"content": content}


@app.put("/notes")
def save_notes(body: NotesBody):
    NOTES_FILE.write_text(body.content, encoding="utf-8")
    return {"ok": True}


# --- AI Assistant ---

SYSTEM_PROMPTS = {
    "summarize": "Summarize the following notes or bullet points concisely. Output only the summary.",
    "cleanup":   "Clean up and rewrite the following text. Fix grammar, improve clarity, preserve meaning. Output only the rewritten text.",
    "expand":    "Expand the following rough idea or bullet points into a more complete, coherent thought. Output only the expanded text.",
}


class AIRequest(BaseModel):
    provider: str      # "anthropic" | "openai_compat"
    model: str
    api_key: str
    base_url: str      # e.g. "http://localhost:11434/v1" for Ollama; "" for OpenAI
    action: str        # "summarize" | "cleanup" | "expand" | "custom"
    custom_prompt: str
    content: str


@app.post("/ai/generate")
def ai_generate(body: AIRequest):
    user_msg = body.content.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Content is empty")

    system = body.custom_prompt.strip() if body.action == "custom" else SYSTEM_PROMPTS.get(body.action, "")
    if not system:
        raise HTTPException(status_code=400, detail=f"Unknown action: {body.action}")

    try:
        if body.provider == "anthropic":
            client = anthropic.Anthropic(api_key=body.api_key)
            msg = client.messages.create(
                model=body.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return {"result": msg.content[0].text}
        else:
            # OpenAI-compatible: OpenAI, Ollama, vLLM, etc.
            kwargs: dict = {"api_key": body.api_key or "ollama"}
            if body.base_url:
                kwargs["base_url"] = body.base_url
            client = openai.OpenAI(**kwargs)
            resp = client.chat.completions.create(
                model=body.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=1024,
            )
            return {"result": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)