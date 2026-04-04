from pathlib import Path
from typing import List

from services.database import get_db

# Directory paths (still needed for static file serving)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
STATIC_DIR = SRC_DIR / "static"


# ── Tasks ──────────────────────────────────────────────────────────────────

async def load_tasks(user_id: str) -> List[dict]:
    """Load all tasks for a user, ordered by position."""
    pool = get_db()
    rows = await pool.fetch(
        "SELECT id, text, checked, position FROM tasks WHERE user_id = $1 ORDER BY position",
        user_id,
    )
    return [{"id": r["id"], "text": r["text"], "checked": r["checked"]} for r in rows]


async def save_task(user_id: str, task_id: str, text: str) -> dict:
    """Create a new task and return it."""
    pool = get_db()
    row = await pool.fetchrow(
        "SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM tasks WHERE user_id = $1",
        user_id,
    )
    position = row["next_pos"]

    await pool.execute(
        "INSERT INTO tasks (id, user_id, text, checked, position) VALUES ($1, $2, $3, FALSE, $4)",
        task_id, user_id, text, position,
    )
    return {"id": task_id, "text": text, "checked": False}


async def update_task(task_id: str, user_id: str, checked: bool) -> dict | None:
    """Toggle a task's checked state and return the updated task."""
    pool = get_db()
    row = await pool.fetchrow(
        "UPDATE tasks SET checked = $1 WHERE id = $2 AND user_id = $3 RETURNING id, text, checked",
        checked, task_id, user_id,
    )
    if not row:
        return None
    return {"id": row["id"], "text": row["text"], "checked": row["checked"]}


async def delete_task(task_id: str, user_id: str) -> bool:
    """Delete a task. Returns True if a row was deleted."""
    pool = get_db()
    result = await pool.execute(
        "DELETE FROM tasks WHERE id = $1 AND user_id = $2",
        task_id, user_id,
    )
    # asyncpg returns e.g. "DELETE 1" or "DELETE 0"
    return result.split()[-1] != "0"


async def reorder_tasks(user_id: str, ids: List[str]) -> List[dict]:
    """Reorder tasks by updating positions, then return the full list."""
    pool = get_db()
    async with pool.acquire() as conn:
        async with conn.transaction():
            for position, task_id in enumerate(ids):
                await conn.execute(
                    "UPDATE tasks SET position = $1 WHERE id = $2 AND user_id = $3",
                    position, task_id, user_id,
                )
    return await load_tasks(user_id)


# ── Notes ──────────────────────────────────────────────────────────────────

async def load_notes(user_id: str) -> str:
    """Load notes for a user."""
    pool = get_db()
    row = await pool.fetchrow(
        "SELECT content FROM notes WHERE user_id = $1",
        user_id,
    )
    return row["content"] if row else ""


async def save_notes(user_id: str, content: str) -> None:
    """Upsert notes for a user."""
    pool = get_db()
    await pool.execute(
        "INSERT INTO notes (user_id, content) VALUES ($1, $2) "
        "ON CONFLICT (user_id) DO UPDATE SET content = $2",
        user_id, content,
    )
