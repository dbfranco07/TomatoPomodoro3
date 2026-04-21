"""Tests for notes CRUD endpoints."""

import pytest
from unittest.mock import patch, AsyncMock

FAKE_NOTE = {"id": "note-001", "title": "My Note", "content": "Hello world"}
FAKE_SUMMARY = {"id": "note-001", "title": "My Note", "updated_at": "2026-01-01T00:00:00"}


# ── GET /notes ─────────────────────────────────────────────────────────────

async def test_list_notes_empty(client):
    with patch("routers.notes.load_notes_list", new=AsyncMock(return_value=[])):
        res = await client.get("/notes")
    assert res.status_code == 200
    assert res.json() == {"notes": []}


async def test_list_notes_returns_list(client):
    with patch("routers.notes.load_notes_list", new=AsyncMock(return_value=[FAKE_SUMMARY])):
        res = await client.get("/notes")
    data = res.json()
    assert len(data["notes"]) == 1
    assert data["notes"][0]["title"] == "My Note"


async def test_list_notes_scoped_to_user(client):
    mock_fn = AsyncMock(return_value=[])
    with patch("routers.notes.load_notes_list", new=mock_fn):
        await client.get("/notes")
    mock_fn.assert_called_once_with("user-test-123")


# ── POST /notes ────────────────────────────────────────────────────────────

async def test_create_note(client):
    with patch("routers.notes.create_note", new=AsyncMock(return_value=FAKE_NOTE)):
        res = await client.post("/notes", json={"title": "My Note"})
    assert res.status_code == 201
    assert res.json()["title"] == "My Note"
    assert res.json()["content"] == "Hello world"


# ── GET /notes/{id} ────────────────────────────────────────────────────────

async def test_get_note(client):
    with patch("routers.notes.load_note", new=AsyncMock(return_value=FAKE_NOTE)):
        res = await client.get("/notes/note-001")
    assert res.status_code == 200
    assert res.json()["content"] == "Hello world"


async def test_get_note_not_found(client):
    with patch("routers.notes.load_note", new=AsyncMock(return_value=None)):
        res = await client.get("/notes/bad-id")
    assert res.status_code == 404


# ── PUT /notes/{id} ────────────────────────────────────────────────────────

async def test_update_note_content(client):
    with patch("routers.notes.save_note", new=AsyncMock(return_value=True)):
        res = await client.put("/notes/note-001", json={"content": "Updated"})
    assert res.status_code == 200
    assert res.json()["ok"] is True


async def test_update_note_not_found(client):
    with patch("routers.notes.save_note", new=AsyncMock(return_value=False)):
        res = await client.put("/notes/bad-id", json={"content": "x"})
    assert res.status_code == 404


# ── PATCH /notes/{id} ─────────────────────────────────────────────────────

async def test_rename_note(client):
    with patch("routers.notes.rename_note", new=AsyncMock(return_value=True)):
        res = await client.patch("/notes/note-001", json={"title": "New Title"})
    assert res.status_code == 200
    assert res.json()["ok"] is True


async def test_rename_note_not_found(client):
    with patch("routers.notes.rename_note", new=AsyncMock(return_value=False)):
        res = await client.patch("/notes/bad-id", json={"title": "x"})
    assert res.status_code == 404


# ── DELETE /notes/{id} ─────────────────────────────────────────────────────

async def test_delete_note(client):
    with patch("routers.notes.delete_note", new=AsyncMock(return_value=True)):
        res = await client.delete("/notes/note-001")
    assert res.status_code == 200
    assert res.json()["ok"] is True


async def test_delete_note_not_found(client):
    with patch("routers.notes.delete_note", new=AsyncMock(return_value=False)):
        res = await client.delete("/notes/bad-id")
    assert res.status_code == 404
