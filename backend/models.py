from pydantic import BaseModel
from typing import List, Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user_id: int
    username: str


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class Message(BaseModel):
    role: str          # "user" | "assistant"
    content: str
    timestamp: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    messages: List[Message]


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: Optional[str] = None


class NewSessionRequest(BaseModel):
    auth_session_id: str  # existing session used for auth
