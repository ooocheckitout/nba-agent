from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class User(BaseModel):
    email: str


class Role(str, Enum):
    assistant = "assistant"
    user = "user"


class Message(BaseModel):
    role: Role
    content: str
    columns: list[str] = Field(default_factory=list)
    data: list[Any] = Field(default_factory=list)


class Suggestion(BaseModel):
    text: str
