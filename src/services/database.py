import os

import asyncpg

_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    """Initialize the asyncpg connection pool and create tables if needed."""
    global _pool
    _pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                text TEXT NOT NULL,
                checked BOOLEAN NOT NULL DEFAULT FALSE,
                position INTEGER NOT NULL DEFAULT 0
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                user_id TEXT PRIMARY KEY REFERENCES users(id),
                content TEXT NOT NULL DEFAULT ''
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                created_at TEXT NOT NULL
            );
        """)


def get_db() -> asyncpg.Pool:
    """Return the active connection pool."""
    assert _pool is not None, "Database not initialized. Call init_db() first."
    return _pool


async def close_db() -> None:
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
