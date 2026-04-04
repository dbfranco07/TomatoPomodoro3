import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from schemas import UserCreate, UserLogin, UserOut
from services.database import get_db
from services.auth import (
    hash_password,
    verify_password,
    create_session_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days


def _set_session_cookie(response: JSONResponse, token: str) -> JSONResponse:
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )
    return response


@router.post("/register")
async def register(body: UserCreate):
    pool = get_db()
    username = body.username.strip()
    if not username or not body.password:
        raise HTTPException(status_code=400, detail="Username and password required")

    existing = await pool.fetchrow("SELECT id FROM users WHERE username = $1", username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    pw_hash = hash_password(body.password)

    token = create_session_token()

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO users (id, username, password_hash, created_at) VALUES ($1, $2, $3, $4)",
                user_id, username, pw_hash, now,
            )
            await conn.execute(
                "INSERT INTO sessions (token, user_id, created_at) VALUES ($1, $2, $3)",
                token, user_id, now,
            )

    user_out = UserOut(id=user_id, username=username)
    response = JSONResponse(content=user_out.model_dump())
    return _set_session_cookie(response, token)


@router.post("/login")
async def login(body: UserLogin):
    pool = get_db()
    row = await pool.fetchrow(
        "SELECT id, username, password_hash FROM users WHERE username = $1",
        body.username.strip(),
    )
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_session_token()
    now = datetime.now(timezone.utc).isoformat()
    await pool.execute(
        "INSERT INTO sessions (token, user_id, created_at) VALUES ($1, $2, $3)",
        token, row["id"], now,
    )

    user_out = UserOut(id=row["id"], username=row["username"])
    response = JSONResponse(content=user_out.model_dump())
    return _set_session_cookie(response, token)


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    pool = get_db()
    await pool.execute("DELETE FROM sessions WHERE user_id = $1", user["id"])

    response = JSONResponse(content={"ok": True})
    response.delete_cookie("session")
    return response


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return UserOut(id=user["id"], username=user["username"])
