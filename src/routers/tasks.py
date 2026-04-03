import uuid
from fastapi import APIRouter, HTTPException
from schemas import TaskCreate, TaskUpdate, TaskReorder
from services.persistence import load_tasks, save_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
def get_tasks():
    return load_tasks()


@router.post("", status_code=201)
def create_task(body: TaskCreate):
    tasks = load_tasks()
    task = {"id": str(uuid.uuid4()),
            "text": body.text.strip(),
            "checked": False}
    tasks.append(task)
    save_tasks(tasks)
    return task


@router.put("/{task_id}")
def update_task(task_id: str, body: TaskUpdate):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["checked"] = body.checked
            save_tasks(tasks)
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/reorder")
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


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    save_tasks(new_tasks)
