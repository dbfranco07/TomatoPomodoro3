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
    """Load all tasks for a user, ordered by position.

    Args:
        user_id: The ID of the user.

    Returns:
        A flat list of task dicts with id, text, checked, parent_id, and details.
    """
    pool = get_db()
    rows = await pool.fetch(
        "SELECT id, text, checked, position, parent_id, details FROM tasks WHERE user_id = $1 ORDER BY position",
        user_id,
    )
    return [
        {
            "id": r["id"],
            "text": r["text"],
            "checked": r["checked"],
            "parent_id": r["parent_id"],
            "details": r["details"],
        }
        for r in rows
    ]


async def save_task(
    user_id: str, task_id: str, text: str, parent_id: str | None = None, details: str = ""
) -> dict:
    """Create a new task and return it.

    Args:
        user_id: The ID of the user.
        task_id: The UUID for the new task.
        text: The task text.
        parent_id: Optional parent task ID (makes this a subtask).
        details: Optional in-depth details for the task.

    Returns:
        A dict with the created task fields.
    """
    pool = get_db()
    row = await pool.fetchrow(
        "SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM tasks WHERE user_id = $1",
        user_id,
    )
    position = row["next_pos"]

    await pool.execute(
        "INSERT INTO tasks (id, user_id, text, checked, position, parent_id, details) VALUES ($1, $2, $3, FALSE, $4, $5, $6)",
        task_id, user_id, text, position, parent_id, details,
    )
    return {"id": task_id, "text": text, "checked": False, "parent_id": parent_id, "details": details}


async def update_task(
    task_id: str, user_id: str, checked: bool | None = None, details: str | None = None
) -> dict | None:
    """Update a task's checked state and/or details.

    Args:
        task_id: The ID of the task.
        user_id: The ID of the user.
        checked: New checked state, or None to leave unchanged.
        details: New details text, or None to leave unchanged.

    Returns:
        The updated task dict, or None if not found.
    """
    pool = get_db()
    sets = []
    params = []
    idx = 1

    if checked is not None:
        sets.append(f"checked = ${idx}")
        params.append(checked)
        idx += 1
    if details is not None:
        sets.append(f"details = ${idx}")
        params.append(details)
        idx += 1

    if not sets:
        return None

    params.append(task_id)
    params.append(user_id)

    query = f"UPDATE tasks SET {', '.join(sets)} WHERE id = ${idx} AND user_id = ${idx + 1} RETURNING id, text, checked, parent_id, details"
    row = await pool.fetchrow(query, *params)
    if not row:
        return None
    return {
        "id": row["id"],
        "text": row["text"],
        "checked": row["checked"],
        "parent_id": row["parent_id"],
        "details": row["details"],
    }


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

async def load_notes_list(user_id: str) -> List[dict]:
    """Load all note summaries for a user, ordered by most recently updated.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of dicts with id, title, and updated_at fields.
    """
    pool = get_db()
    rows = await pool.fetch(
        "SELECT id, title, updated_at FROM notes WHERE user_id = $1 ORDER BY updated_at DESC",
        user_id,
    )
    return [
        {"id": r["id"], "title": r["title"], "updated_at": r["updated_at"].isoformat()}
        for r in rows
    ]


async def load_note(user_id: str, note_id: str) -> dict | None:
    """Load a single note's full content.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note.

    Returns:
        A dict with id, title, and content, or None if not found.
    """
    pool = get_db()
    row = await pool.fetchrow(
        "SELECT id, title, content FROM notes WHERE id = $1 AND user_id = $2",
        note_id, user_id,
    )
    if not row:
        return None
    return {"id": row["id"], "title": row["title"], "content": row["content"]}


async def create_note(user_id: str, note_id: str, title: str) -> dict:
    """Create a new note and return it.

    Args:
        user_id: The ID of the user.
        note_id: The UUID for the new note.
        title: The title of the note.

    Returns:
        A dict with id, title, and content fields.
    """
    pool = get_db()
    await pool.execute(
        "INSERT INTO notes (id, user_id, title, content, updated_at) VALUES ($1, $2, $3, '', NOW())",
        note_id, user_id, title,
    )
    return {"id": note_id, "title": title, "content": ""}


async def save_note(user_id: str, note_id: str, content: str) -> bool:
    """Update a note's content.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note.
        content: The new content.

    Returns:
        True if the note was found and updated.
    """
    pool = get_db()
    result = await pool.execute(
        "UPDATE notes SET content = $1, updated_at = NOW() WHERE id = $2 AND user_id = $3",
        content, note_id, user_id,
    )
    return result.split()[-1] != "0"


async def rename_note(user_id: str, note_id: str, title: str) -> bool:
    """Rename a note.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note.
        title: The new title.

    Returns:
        True if the note was found and renamed.
    """
    pool = get_db()
    result = await pool.execute(
        "UPDATE notes SET title = $1, updated_at = NOW() WHERE id = $2 AND user_id = $3",
        title, note_id, user_id,
    )
    return result.split()[-1] != "0"


async def delete_note(user_id: str, note_id: str) -> bool:
    """Delete a note.

    Args:
        user_id: The ID of the user.
        note_id: The ID of the note.

    Returns:
        True if a row was deleted.
    """
    pool = get_db()
    result = await pool.execute(
        "DELETE FROM notes WHERE id = $1 AND user_id = $2",
        note_id, user_id,
    )
    return result.split()[-1] != "0"
