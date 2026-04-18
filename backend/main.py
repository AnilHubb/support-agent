import json
import logging
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import (
    LoginRequest, LoginResponse,
    ChatRequest, ChatResponse,
    SessionResponse, SessionSummary, NewSessionRequest,
    Message,
)
from database import init_db, get_db
from auth import authenticate_user, create_session, get_user_from_session
from agent import ChatAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s: %(message)s",
)
logger = logging.getLogger("support-chatbot")

app = FastAPI(title="Customer Support Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialised with seed data.")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if not req.username or not req.password:
        raise HTTPException(400, "Username and password are required.")

    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(401, "Invalid username or password.")

    session_id = create_session(user["id"])
    now = datetime.utcnow().isoformat()

    conn = get_db()
    conn.execute(
        "INSERT INTO chat_sessions (session_id, user_id, messages, title, created_at) VALUES (?,?,?,?,?)",
        (session_id, user["id"], "[]", "New Chat", now),
    )
    conn.commit()
    conn.close()

    logger.info("User '%s' logged in — session %s", user["username"], session_id)
    return LoginResponse(session_id=session_id, user_id=user["id"], username=user["username"])


# ---------------------------------------------------------------------------
# Sessions list + new session
# ---------------------------------------------------------------------------
@app.get("/sessions", response_model=List[SessionSummary])
def list_sessions(auth_session_id: str):
    user_id = get_user_from_session(auth_session_id)
    if not user_id:
        raise HTTPException(401, "Invalid or expired session.")

    conn = get_db()
    rows = conn.execute(
        "SELECT session_id, title, created_at FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    return [SessionSummary(session_id=r["session_id"], title=r["title"], created_at=r["created_at"]) for r in rows]


@app.post("/session/new", response_model=SessionSummary)
def new_session(req: NewSessionRequest):
    user_id = get_user_from_session(req.auth_session_id)
    if not user_id:
        raise HTTPException(401, "Invalid or expired session.")

    new_sid = create_session(user_id)
    now = datetime.utcnow().isoformat()

    conn = get_db()
    conn.execute(
        "INSERT INTO chat_sessions (session_id, user_id, messages, title, created_at) VALUES (?,?,?,?,?)",
        (new_sid, user_id, "[]", "New Chat", now),
    )
    conn.commit()
    conn.close()

    logger.info("New session %s created for user_id=%d", new_sid, user_id)
    return SessionSummary(session_id=new_sid, title="New Chat", created_at=now)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Message cannot be empty.")

    user_id = get_user_from_session(req.session_id)
    if not user_id:
        raise HTTPException(401, "Invalid or expired session.")

    conn = get_db()
    row = conn.execute(
        "SELECT messages, title FROM chat_sessions WHERE session_id = ?", (req.session_id,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(404, "Session not found.")

    history: list = json.loads(row["messages"])
    is_first_message = len(history) == 0

    try:
        agent = ChatAgent(user_id=user_id)
        reply = agent.chat(req.message, history)
    except EnvironmentError as exc:
        conn.close()
        raise HTTPException(503, str(exc))
    except Exception as exc:
        logger.exception("Agent error: %s", exc)
        conn.close()
        raise HTTPException(500, "The AI agent encountered an error. Please try again.")

    now = datetime.utcnow().isoformat()
    history.append({"role": "user",      "content": req.message, "timestamp": now})
    history.append({"role": "assistant", "content": reply,       "timestamp": now})

    # Auto-title from first message (truncate to 40 chars)
    title = row["title"]
    if is_first_message:
        title = req.message[:40] + ("…" if len(req.message) > 40 else "")

    conn.execute(
        "UPDATE chat_sessions SET messages=?, title=? WHERE session_id=?",
        (json.dumps(history), title, req.session_id),
    )
    conn.commit()
    conn.close()

    logger.info("session=%s  msg=%r  reply_len=%d", req.session_id, req.message[:50], len(reply))
    return ChatResponse(response=reply, session_id=req.session_id)


# ---------------------------------------------------------------------------
# Session detail
# ---------------------------------------------------------------------------
@app.get("/session/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    user_id = get_user_from_session(session_id)
    if not user_id:
        raise HTTPException(401, "Invalid or expired session.")

    conn = get_db()
    row = conn.execute(
        "SELECT session_id, user_id, messages FROM chat_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, "Session not found.")

    messages = [Message(**m) for m in json.loads(row["messages"])]
    return SessionResponse(session_id=row["session_id"], user_id=row["user_id"], messages=messages)
