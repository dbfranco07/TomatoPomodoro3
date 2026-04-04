import secrets
import bcrypt
from fastapi import HTTPException, Request
from services.database import get_db


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = get_db()
    cursor = await db.execute(
        "SELECT u.id, u.username FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?",
        (token,),
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"id": row["id"], "username": row["username"]}
