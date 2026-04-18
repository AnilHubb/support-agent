import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_PATH = "support.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            product_name TEXT NOT NULL,
            delivery_date TEXT,
            estimated_delivery TEXT,
            tracking_number TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            messages TEXT DEFAULT '[]',
            title TEXT DEFAULT 'New Chat',
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Add title column if upgrading from old schema
    try:
        cursor.execute("ALTER TABLE chat_sessions ADD COLUMN title TEXT DEFAULT 'New Chat'")
    except Exception:
        pass  # Column already exists

    conn.commit()

    # --- Seed users ---
    seed_users = [
        (1, "alice",   hash_password("alice123"),   "alice@example.com"),
        (2, "bob",     hash_password("bob123"),     "bob@example.com"),
        (3, "charlie", hash_password("charlie123"), "charlie@example.com"),
    ]
    for u in seed_users:
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash, email) VALUES (?, ?, ?, ?)", u
        )

    # --- Seed orders ---
    today = datetime.now()
    seed_orders = [
        ("ORD-001", 1, "shipped",          "Wireless Headphones", None,
         (today + timedelta(days=2)).strftime("%Y-%m-%d"),  "TRK123456"),
        ("ORD-002", 1, "delivered",        "Smart Watch",
         (today - timedelta(days=1)).strftime("%Y-%m-%d"),
         (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "TRK789012"),
        ("ORD-003", 2, "out_for_delivery", "Laptop Stand",         None,
         today.strftime("%Y-%m-%d"),                         "TRK345678"),
        ("ORD-004", 2, "delayed",          "Gaming Mouse",         None,
         (today + timedelta(days=5)).strftime("%Y-%m-%d"),  "TRK901234"),
        ("ORD-005", 3, "shipped",          "Mechanical Keyboard",  None,
         (today + timedelta(days=3)).strftime("%Y-%m-%d"),  "TRK567890"),
        ("ORD-006", 1, "processing",       "USB Hub",              None,
         (today + timedelta(days=4)).strftime("%Y-%m-%d"),  None),
        ("ORD-007", 2, "delivered",        "Monitor",
         (today - timedelta(days=3)).strftime("%Y-%m-%d"),
         (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "TRK111222"),
        ("ORD-008", 3, "out_for_delivery", "Office Chair",         None,
         today.strftime("%Y-%m-%d"),                         "TRK333444"),
        ("ORD-009", 3, "delayed",          "Standing Desk",        None,
         (today + timedelta(days=7)).strftime("%Y-%m-%d"),  "TRK555666"),
        ("ORD-010", 1, "cancelled",        "Phone Case",           None, None, None),
    ]
    for o in seed_orders:
        cursor.execute(
            """INSERT OR IGNORE INTO orders
               (order_id, user_id, status, product_name, delivery_date, estimated_delivery, tracking_number)
               VALUES (?, ?, ?, ?, ?, ?, ?)""", o
        )

    conn.commit()
    conn.close()
