from typing import List
from pydantic import BaseModel


class TaskCreate(BaseModel):
    text: str


class TaskUpdate(BaseModel):
    checked: bool


class TaskReorder(BaseModel):
    ids: List[str]


class NotesBody(BaseModel):
    content: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str


class AIRequest(BaseModel):
    provider: str       # "anthropic" | "openai_compat"
    model: str
    api_key: str
    base_url: str       # e.g. "http://localhost:11434/v1" for Ollama; "" for OpenAI
    action: str         # "summarize" | "cleanup" | "expand" | "custom"
    custom_prompt: str
    content: str
