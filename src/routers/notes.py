import uuid

from fastapi import APIRouter, Depends, HTTPException
from schemas import NoteCreate, NoteUpdate, NoteRename
from services.auth import get_current_user
from services.persistence import (
    load_notes_list, load_note, create_note, save_note, rename_note, delete_note,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("")
async def list_notes(user=Depends(get_current_user)):
    """Return all notes for the current user (id, title, updated_at)."""
    return {"notes": await load_notes_list(user["id"])}


@router.post("", status_code=201)
async def create_new_note(body: NoteCreate, user=Depends(get_current_user)):
    """Create a new named note."""
    note_id = str(uuid.uuid4())
    note = await create_note(user["id"], note_id, body.title)
    return note


@router.get("/{note_id}")
async def get_note(note_id: str, user=Depends(get_current_user)):
    """Get a single note's full content."""
    note = await load_note(user["id"], note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}")
async def update_note_content(note_id: str, body: NoteUpdate, user=Depends(get_current_user)):
    """Update a note's content (used by auto-save)."""
    ok = await save_note(user["id"], note_id, body.content)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}


@router.patch("/{note_id}")
async def rename_existing_note(note_id: str, body: NoteRename, user=Depends(get_current_user)):
    """Rename a note."""
    ok = await rename_note(user["id"], note_id, body.title)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}


@router.delete("/{note_id}")
async def delete_existing_note(note_id: str, user=Depends(get_current_user)):
    """Delete a note."""
    ok = await delete_note(user["id"], note_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}
