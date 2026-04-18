import uuid
from database import get_db, hash_password

# In-memory session store: session_id -> user_id
_sessions: dict[str, int] = {}


def authenticate_user(username: str, password: str):
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password)),
    ).fetchone()
    conn.close()
    return user


def create_session(user_id: int) -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = user_id
    return session_id


def get_user_from_session(session_id: str) -> int | None:
    return _sessions.get(session_id)
