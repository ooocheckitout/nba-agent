from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class User(BaseModel):
    email: str


class Role(str, Enum):
    assistant = "assistant"
    user = "user"


class TextMessage(BaseModel):
    text: str


class DataMessage(BaseModel):
    title: str
    glossary: dict[str, str]
    columns: list[str]
    data: list[Any]


class Message(BaseModel):
    role: Role
    content: list[TextMessage | DataMessage]


class Suggestion(BaseModel):
    text: str
