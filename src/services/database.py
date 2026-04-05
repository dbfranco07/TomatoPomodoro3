"""asyncpg connection pool management for TomatoPomodoro."""

import os
from urllib.parse import urlparse, unquote

import asyncpg

_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    """Initialize the asyncpg connection pool from DATABASE_URL.

    Reads the ``DATABASE_URL`` environment variable, parses connection
    parameters, and opens a pool stored in the module-level ``_pool``.
    """
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
    """Return the active asyncpg connection pool.

    Returns:
        The initialized connection pool.

    Raises:
        AssertionError: If ``init_db()`` has not been called yet.
    """
    assert _pool is not None, (
        "Database not initialized. Call init_db() first."
    )
    return _pool


async def close_db() -> None:
    """Close and release the asyncpg connection pool.

    After this call, ``_pool`` is set to None. Safe to call even if
    the pool was never opened.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
