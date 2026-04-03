from fastapi import APIRouter
from schemas import NotesBody
from services.persistence import load_notes, save_notes

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("")
def get_notes():
    return {"content": load_notes()}


@router.put("")
def put_notes(body: NotesBody):
    save_notes(body.content)
    return {"ok": True}
