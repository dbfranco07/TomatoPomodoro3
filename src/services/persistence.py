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
    db = get_db()
    cursor = await db.execute(
        "SELECT id, text, checked, position FROM tasks WHERE user_id = ? ORDER BY position",
        (user_id,),
    )
    rows = await cursor.fetchall()
    return [{"id": r["id"], "text": r["text"], "checked": bool(r["checked"])} for r in rows]


async def save_task(user_id: str, task_id: str, text: str) -> dict:
    db = get_db()
    # Set position to max+1 for this user
    cursor = await db.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM tasks WHERE user_id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    position = row["next_pos"]

    await db.execute(
        "INSERT INTO tasks (id, user_id, text, checked, position) VALUES (?, ?, ?, 0, ?)",
        (task_id, user_id, text, position),
    )
    await db.commit()
    return {"id": task_id, "text": text, "checked": False}


async def update_task(task_id: str, user_id: str, checked: bool) -> dict | None:
    db = get_db()
    cursor = await db.execute(
        "UPDATE tasks SET checked = ? WHERE id = ? AND user_id = ? RETURNING id, text, checked",
        (int(checked), task_id, user_id),
    )
    row = await cursor.fetchone()
    await db.commit()
    if not row:
        return None
    return {"id": row["id"], "text": row["text"], "checked": bool(row["checked"])}


async def delete_task(task_id: str, user_id: str) -> bool:
    db = get_db()
    cursor = await db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def reorder_tasks(user_id: str, ids: List[str]) -> List[dict]:
    db = get_db()
    for position, task_id in enumerate(ids):
        await db.execute(
            "UPDATE tasks SET position = ? WHERE id = ? AND user_id = ?",
            (position, task_id, user_id),
        )
    await db.commit()
    return await load_tasks(user_id)


# ── Notes ──────────────────────────────────────────────────────────────────

async def load_notes(user_id: str) -> str:
    db = get_db()
    cursor = await db.execute(
        "SELECT content FROM notes WHERE user_id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    return row["content"] if row else ""


async def save_notes(user_id: str, content: str) -> None:
    db = get_db()
    await db.execute(
        "INSERT OR REPLACE INTO notes (user_id, content) VALUES (?, ?)",
        (user_id, content),
    )
    await db.commit()
