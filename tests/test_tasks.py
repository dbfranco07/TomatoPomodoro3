"""Tests for task CRUD endpoints."""

import pytest
from unittest.mock import patch, AsyncMock

FAKE_TASK = {
    "id": "task-001",
    "text": "Buy milk",
    "checked": False,
    "parent_id": None,
    "details": "",
}


# ── GET /tasks ─────────────────────────────────────────────────────────────

async def test_get_tasks_empty(client):
    with patch("routers.tasks.load_tasks", new=AsyncMock(return_value=[])):
        res = await client.get("/tasks")
    assert res.status_code == 200
    assert res.json() == []


async def test_get_tasks_returns_list(client):
    with patch("routers.tasks.load_tasks", new=AsyncMock(return_value=[FAKE_TASK])):
        res = await client.get("/tasks")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["text"] == "Buy milk"


async def test_get_tasks_scoped_to_user(client):
    mock_load = AsyncMock(return_value=[])
    with patch("routers.tasks.load_tasks", new=mock_load):
        await client.get("/tasks")
    mock_load.assert_called_once_with("user-test-123")


# ── POST /tasks ────────────────────────────────────────────────────────────

async def test_create_task(client):
    with patch("routers.tasks.save_task", new=AsyncMock(return_value=FAKE_TASK)):
        res = await client.post("/tasks", json={"text": "Buy milk"})
    assert res.status_code == 201
    assert res.json()["text"] == "Buy milk"


async def test_create_task_strips_whitespace(client):
    captured = {}

    async def mock_save(user_id, task_id, text, parent_id=None, details=""):
        captured["text"] = text
        return {**FAKE_TASK, "text": text}

    with patch("routers.tasks.save_task", new=mock_save):
        await client.post("/tasks", json={"text": "  padded  "})

    assert captured["text"] == "padded"


async def test_create_subtask(client):
    subtask = {**FAKE_TASK, "id": "task-002", "parent_id": "task-001"}
    with patch("routers.tasks.save_task", new=AsyncMock(return_value=subtask)):
        res = await client.post(
            "/tasks",
            json={"text": "Sub item", "parent_id": "task-001"},
        )
    assert res.status_code == 201
    assert res.json()["parent_id"] == "task-001"


# ── PUT /tasks/{id} ────────────────────────────────────────────────────────

async def test_update_task_checked(client):
    updated = {**FAKE_TASK, "checked": True}
    with patch("routers.tasks.update_task", new=AsyncMock(return_value=updated)):
        res = await client.put("/tasks/task-001", json={"checked": True})
    assert res.status_code == 200
    assert res.json()["checked"] is True


async def test_update_task_not_found(client):
    with patch("routers.tasks.update_task", new=AsyncMock(return_value=None)):
        res = await client.put("/tasks/bad-id", json={"checked": True})
    assert res.status_code == 404


async def test_update_task_details(client):
    updated = {**FAKE_TASK, "details": "Some notes"}
    with patch("routers.tasks.update_task", new=AsyncMock(return_value=updated)):
        res = await client.put("/tasks/task-001", json={"details": "Some notes"})
    assert res.status_code == 200
    assert res.json()["details"] == "Some notes"


# ── POST /tasks/reorder ────────────────────────────────────────────────────

async def test_reorder_tasks(client):
    reordered = [FAKE_TASK]
    with patch("routers.tasks.reorder_tasks", new=AsyncMock(return_value=reordered)):
        res = await client.post("/tasks/reorder", json={"ids": ["task-001"]})
    assert res.status_code == 200
    assert len(res.json()) == 1


# ── DELETE /tasks/{id} ─────────────────────────────────────────────────────

async def test_delete_task(client):
    with patch("routers.tasks.delete_task", new=AsyncMock(return_value=True)):
        res = await client.delete("/tasks/task-001")
    assert res.status_code == 204


async def test_delete_task_not_found(client):
    with patch("routers.tasks.delete_task", new=AsyncMock(return_value=False)):
        res = await client.delete("/tasks/bad-id")
    assert res.status_code == 404
