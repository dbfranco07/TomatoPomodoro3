"""Task CRUD endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException

from schemas import TaskCreate, TaskUpdate, TaskReorder
from services.auth import get_current_user
from services.persistence import (
    load_tasks,
    save_task,
    update_task,
    delete_task,
    reorder_tasks,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
async def get_tasks(
    user: dict = Depends(get_current_user),
) -> list[dict]:
    """Get all tasks for the current user, including subtasks.

    Args:
        user: The authenticated user dict from the session.

    Returns:
        A list of task dicts ordered by position.
    """
    return await load_tasks(user["id"])


@router.post("", status_code=201)
async def create_task(
    body: TaskCreate,
    user: dict = Depends(get_current_user),
) -> dict:
    """Create a task or subtask.

    Args:
        body: Task creation payload.
        user: The authenticated user dict from the session.

    Returns:
        The newly created task dict.
    """
    task_id = str(uuid.uuid4())
    return await save_task(
        user["id"], task_id, body.text.strip(),
        parent_id=body.parent_id, details=body.details,
    )


@router.put("/{task_id}")
async def update_task_endpoint(
    task_id: str,
    body: TaskUpdate,
    user: dict = Depends(get_current_user),
) -> dict:
    """Update a task's checked state and/or details.

    Args:
        task_id: The ID of the task to update.
        body: Fields to update.
        user: The authenticated user dict from the session.

    Returns:
        The updated task dict.

    Raises:
        HTTPException: 404 if the task is not found.
    """
    result = await update_task(
        task_id, user["id"],
        checked=body.checked, details=body.details,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.post("/reorder")
async def reorder(
    body: TaskReorder,
    user: dict = Depends(get_current_user),
) -> list[dict]:
    """Reorder tasks by position.

    Args:
        body: Ordered list of task IDs.
        user: The authenticated user dict from the session.

    Returns:
        The full updated list of task dicts.
    """
    return await reorder_tasks(user["id"], body.ids)


@router.delete("/{task_id}", status_code=204)
async def remove_task(
    task_id: str,
    user: dict = Depends(get_current_user),
) -> None:
    """Delete a task and its subtasks (via CASCADE).

    Args:
        task_id: The ID of the task to delete.
        user: The authenticated user dict from the session.

    Raises:
        HTTPException: 404 if the task is not found.
    """
    deleted = await delete_task(task_id, user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
