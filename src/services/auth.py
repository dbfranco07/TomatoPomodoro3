"""Authentication helpers: password hashing, session tokens, and
the FastAPI dependency for retrieving the current user.
"""

import secrets

import bcrypt
from fastapi import HTTPException, Request

from services.database import get_db


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: The plaintext password to hash.

    Returns:
        A bcrypt-hashed password string.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        password: The plaintext password to check.
        password_hash: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_session_token() -> str:
    """Generate a cryptographically secure URL-safe session token.

    Returns:
        A 32-byte URL-safe random token string.
    """
    return secrets.token_urlsafe(32)


async def get_current_user(request: Request) -> dict:
    """Resolve the currently authenticated user from the session cookie.

    Args:
        request: The incoming FastAPI request.

    Returns:
        A dict with ``id`` and ``username`` keys for the current user.

    Raises:
        HTTPException: 401 if no session cookie is present or the
            session token is invalid or expired.
    """
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    pool = get_db()
    row = await pool.fetchrow(
        "SELECT u.id, u.username "
        "FROM sessions s JOIN users u ON s.user_id = u.id "
        "WHERE s.token = $1",
        token,
    )
    if not row:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"id": row["id"], "username": row["username"]}
