import os
from urllib.parse import urlparse, unquote

import asyncpg

_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    """Initialize the asyncpg connection pool and create tables if needed."""
    global _pool
    parsed = urlparse(os.environ["DATABASE_URL"])
    _pool = await asyncpg.create_pool(
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        statement_cache_size=0,
    )


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
