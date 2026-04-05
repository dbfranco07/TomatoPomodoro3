"""Notes CRUD endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException

from schemas import NoteCreate, NoteUpdate, NoteRename
from services.auth import get_current_user
from services.persistence import (
    load_notes_list,
    load_note,
    create_note,
    save_note,
    rename_note,
    delete_note,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("")
async def list_notes(
    user: dict = Depends(get_current_user),
) -> dict:
    """Return all notes for the current user.

    Args:
        user: The authenticated user dict from the session.

    Returns:
        A dict with a ``notes`` key containing a list of note
        summaries (id, title, updated_at).
    """
    return {"notes": await load_notes_list(user["id"])}


@router.post("", status_code=201)
async def create_new_note(
    body: NoteCreate,
    user: dict = Depends(get_current_user),
) -> dict:
    """Create a new named note.

    Args:
        body: Note creation payload with a title.
        user: The authenticated user dict from the session.

    Returns:
        The newly created note dict (id, title, content).
    """
    note_id = str(uuid.uuid4())
    note = await create_note(user["id"], note_id, body.title)
    return note


@router.get("/{note_id}")
async def get_note(
    note_id: str,
    user: dict = Depends(get_current_user),
) -> dict:
    """Get a single note's full content.

    Args:
        note_id: The ID of the note to retrieve.
        user: The authenticated user dict from the session.

    Returns:
        The note dict (id, title, content).

    Raises:
        HTTPException: 404 if the note is not found.
    """
    note = await load_note(user["id"], note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}")
async def update_note_content(
    note_id: str,
    body: NoteUpdate,
    user: dict = Depends(get_current_user),
) -> dict:
    """Update a note's content (used by auto-save).

    Args:
        note_id: The ID of the note to update.
        body: New content payload.
        user: The authenticated user dict from the session.

    Returns:
        A dict with ``ok: True`` on success.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    ok = await save_note(user["id"], note_id, body.content)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}


@router.patch("/{note_id}")
async def rename_existing_note(
    note_id: str,
    body: NoteRename,
    user: dict = Depends(get_current_user),
) -> dict:
    """Rename a note.

    Args:
        note_id: The ID of the note to rename.
        body: New title payload.
        user: The authenticated user dict from the session.

    Returns:
        A dict with ``ok: True`` on success.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    ok = await rename_note(user["id"], note_id, body.title)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}


@router.delete("/{note_id}")
async def delete_existing_note(
    note_id: str,
    user: dict = Depends(get_current_user),
) -> dict:
    """Delete a note.

    Args:
        note_id: The ID of the note to delete.
        user: The authenticated user dict from the session.

    Returns:
        A dict with ``ok: True`` on success.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    ok = await delete_note(user["id"], note_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}
