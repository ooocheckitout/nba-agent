from enum import Enum
from pydantic import BaseModel


class User(BaseModel):
    email: str


class Role(str, Enum):
    assistant = "assistant"
    user = "user"


class Message(BaseModel):
    role: Role
    content: str


class Suggestion(BaseModel):
    text: str
