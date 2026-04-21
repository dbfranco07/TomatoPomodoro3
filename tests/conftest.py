"""Shared fixtures for all backend tests."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

import services.database as _db_module

FAKE_USER = {"id": "user-test-123", "username": "testuser"}


def _make_pool():
    """Return a (pool, conn) pair of asyncpg-shaped mocks.

    The pool supports the acquire() async-CM pattern used by
    reorder_tasks and register, plus the standard fetch/fetchrow/execute
    methods on both the pool and the inner connection.
    """
    pool = AsyncMock()
    conn = AsyncMock()

    # pool.acquire() is a sync call returning an async context manager
    acquire_cm = AsyncMock()
    acquire_cm.__aenter__ = AsyncMock(return_value=conn)
    acquire_cm.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=acquire_cm)

    # conn.transaction() is a sync call returning an async context manager
    txn_cm = AsyncMock()
    txn_cm.__aenter__ = AsyncMock(return_value=txn_cm)
    txn_cm.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=txn_cm)

    # Safe defaults
    pool.fetchrow = AsyncMock(return_value=None)
    pool.fetch = AsyncMock(return_value=[])
    pool.execute = AsyncMock(return_value="DELETE 0")
    conn.execute = AsyncMock(return_value="INSERT 1")

    return pool, conn


@pytest_asyncio.fixture
async def client():
    """Authenticated async HTTP client with a mocked DB pool."""
    import main as _main
    from services.auth import get_current_user

    pool, conn = _make_pool()
    _db_module._pool = pool

    with patch.object(_main, "init_db", new=AsyncMock()), \
         patch.object(_main, "close_db", new=AsyncMock()):
        _main.app.dependency_overrides[get_current_user] = lambda: FAKE_USER
        async with AsyncClient(
            transport=ASGITransport(app=_main.app),
            base_url="http://test",
        ) as ac:
            ac.pool = pool
            ac.conn = conn
            yield ac
        _main.app.dependency_overrides.clear()

    _db_module._pool = None


@pytest_asyncio.fixture
async def raw_client():
    """Unauthenticated async HTTP client for auth-endpoint tests."""
    import main as _main

    pool, conn = _make_pool()
    _db_module._pool = pool

    with patch.object(_main, "init_db", new=AsyncMock()), \
         patch.object(_main, "close_db", new=AsyncMock()):
        async with AsyncClient(
            transport=ASGITransport(app=_main.app),
            base_url="http://test",
        ) as ac:
            ac.pool = pool
            ac.conn = conn
            yield ac

    _db_module._pool = None
