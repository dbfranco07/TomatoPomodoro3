import json
from pathlib import Path
from typing import List

# persistence.py lives at src/services/persistence.py
# .parent       -> src/services/
# .parent.parent -> src/
# .parent.parent.parent -> TomatoPomodoro3/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
STATIC_DIR = SRC_DIR / "static"
TASKS_FILE = SRC_DIR / "tasks.json"
NOTES_FILE = SRC_DIR / "notes.txt"


def load_tasks() -> List[dict]:
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]")
    return json.loads(TASKS_FILE.read_text())


def save_tasks(tasks: List[dict]) -> None:
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


def load_notes() -> str:
    return NOTES_FILE.read_text(encoding="utf-8") if NOTES_FILE.exists() else ""


def save_notes(content: str) -> None:
    NOTES_FILE.write_text(content, encoding="utf-8")
