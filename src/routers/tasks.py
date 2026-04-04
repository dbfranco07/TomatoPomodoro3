import uuid
from fastapi import APIRouter, Depends, HTTPException
from schemas import TaskCreate, TaskUpdate, TaskReorder
from services.auth import get_current_user
from services.persistence import load_tasks, save_task, update_task, delete_task, reorder_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
async def get_tasks(user=Depends(get_current_user)):
    return await load_tasks(user["id"])


@router.post("", status_code=201)
async def create_task(body: TaskCreate, user=Depends(get_current_user)):
    task_id = str(uuid.uuid4())
    return await save_task(user["id"], task_id, body.text.strip())


@router.put("/{task_id}")
async def toggle_task(task_id: str, body: TaskUpdate, user=Depends(get_current_user)):
    result = await update_task(task_id, user["id"], body.checked)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.post("/reorder")
async def reorder(body: TaskReorder, user=Depends(get_current_user)):
    return await reorder_tasks(user["id"], body.ids)


@router.delete("/{task_id}", status_code=204)
async def remove_task(task_id: str, user=Depends(get_current_user)):
    deleted = await delete_task(task_id, user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
