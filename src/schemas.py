"""Pydantic request/response schemas for TomatoPomodoro."""

from pydantic import BaseModel


class TaskCreate(BaseModel):
    """Payload for creating a new task.

    Attributes:
        text: The display text of the task.
        parent_id: ID of the parent task, or None for a root task.
        details: Extended details for the task.
    """

    text: str
    parent_id: str | None = None
    details: str = ""


class TaskUpdate(BaseModel):
    """Payload for updating a task's state.

    Attributes:
        checked: New checked state, or None to leave unchanged.
        details: New details text, or None to leave unchanged.
    """

    checked: bool | None = None
    details: str | None = None


class TaskReorder(BaseModel):
    """Payload for reordering tasks.

    Attributes:
        ids: Task IDs in the desired display order.
    """

    ids: list[str]


class NotesBody(BaseModel):
    """Generic note content payload.

    Attributes:
        content: The note body text.
    """

    content: str


class NoteCreate(BaseModel):
    """Payload for creating a new note.

    Attributes:
        title: The title of the new note.
    """

    title: str


class NoteUpdate(BaseModel):
    """Payload for updating a note's content.

    Attributes:
        content: The new note body text.
    """

    content: str


class NoteRename(BaseModel):
    """Payload for renaming a note.

    Attributes:
        title: The new title.
    """

    title: str


class UserCreate(BaseModel):
    """Payload for registering a new user.

    Attributes:
        username: The desired username.
        password: The plaintext password.
    """

    username: str
    password: str


class UserLogin(BaseModel):
    """Payload for logging in.

    Attributes:
        username: The user's username.
        password: The plaintext password.
    """

    username: str
    password: str


class UserOut(BaseModel):
    """Public representation of an authenticated user.

    Attributes:
        id: The user's UUID.
        username: The user's username.
    """

    id: str
    username: str


class AIRequest(BaseModel):
    """Payload for an AI text-generation request.

    Attributes:
        provider: AI backend; ``"anthropic"`` or ``"openai_compat"``.
        model: Model identifier (e.g. ``"claude-3-5-sonnet-20241022"``).
        api_key: API key for the chosen provider.
        base_url: Base URL for OpenAI-compatible APIs (e.g.
            ``"http://localhost:11434/v1"`` for Ollama).
            Pass an empty string for the default OpenAI endpoint.
        action: Generation mode; one of ``"summarize"``, ``"cleanup"``,
            ``"expand"``, or ``"custom"``.
        custom_prompt: System prompt used when action is ``"custom"``.
        content: The user text to process.
    """

    provider: str
    model: str
    api_key: str
    base_url: str
    action: str
    custom_prompt: str
    content: str
