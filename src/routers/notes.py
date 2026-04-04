from fastapi import APIRouter, Depends
from schemas import NotesBody
from services.auth import get_current_user
from services.persistence import load_notes, save_notes

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("")
async def get_notes(user=Depends(get_current_user)):
    return {"content": await load_notes(user["id"])}


@router.put("")
async def put_notes(body: NotesBody, user=Depends(get_current_user)):
    await save_notes(user["id"], body.content)
    return {"ok": True}
