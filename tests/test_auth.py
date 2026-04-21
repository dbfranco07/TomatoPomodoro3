"""Tests for authentication endpoints."""

import bcrypt
import pytest
from unittest.mock import AsyncMock, patch


# ── /auth/register ─────────────────────────────────────────────────────────

async def test_register_success(raw_client):
    # No existing user found
    raw_client.pool.fetchrow.return_value = None

    res = await raw_client.post(
        "/auth/register",
        json={"username": "alice", "password": "secret"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "alice"
    assert "id" in data


async def test_register_duplicate_username(raw_client):
    # Simulate a pre-existing user
    raw_client.pool.fetchrow.return_value = {"id": "existing-id"}

    res = await raw_client.post(
        "/auth/register",
        json={"username": "alice", "password": "secret"},
    )
    assert res.status_code == 409
    assert "taken" in res.json()["detail"].lower()


async def test_register_empty_fields(raw_client):
    res = await raw_client.post(
        "/auth/register",
        json={"username": "", "password": ""},
    )
    assert res.status_code == 400


# ── /auth/login ────────────────────────────────────────────────────────────

async def test_login_success(raw_client):
    pw_hash = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
    raw_client.pool.fetchrow.return_value = {
        "id": "user-abc",
        "username": "alice",
        "password_hash": pw_hash,
    }
    raw_client.pool.execute = AsyncMock(return_value="INSERT 1")

    res = await raw_client.post(
        "/auth/login",
        json={"username": "alice", "password": "secret"},
    )
    assert res.status_code == 200
    assert res.json()["username"] == "alice"


async def test_login_wrong_password(raw_client):
    pw_hash = bcrypt.hashpw(b"correct", bcrypt.gensalt()).decode()
    raw_client.pool.fetchrow.return_value = {
        "id": "user-abc",
        "username": "alice",
        "password_hash": pw_hash,
    }

    res = await raw_client.post(
        "/auth/login",
        json={"username": "alice", "password": "wrong"},
    )
    assert res.status_code == 401


async def test_login_unknown_user(raw_client):
    raw_client.pool.fetchrow.return_value = None

    res = await raw_client.post(
        "/auth/login",
        json={"username": "nobody", "password": "x"},
    )
    assert res.status_code == 401


# ── /auth/me ───────────────────────────────────────────────────────────────

async def test_me_authenticated(client):
    res = await client.get("/auth/me")
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "testuser"
    assert data["id"] == "user-test-123"


async def test_me_unauthenticated(raw_client):
    # No session cookie set — raw_client has no auth override
    raw_client.pool.fetchrow.return_value = None
    res = await raw_client.get("/auth/me")
    assert res.status_code == 401


# ── /auth/logout ───────────────────────────────────────────────────────────

async def test_logout(client):
    client.pool.execute = AsyncMock(return_value="DELETE 1")
    res = await client.post("/auth/logout")
    assert res.status_code == 200
    assert res.json()["ok"] is True
