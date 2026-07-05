"""Database operations module for TradeChill.

Uses SQLite via stdlib sqlite3. Database is stored at ~/.tradechill/tradechill.db.
All tables are created on first import if they don't exist.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any, Generator, Optional
from .utils import get_db_path


# Schema definitions
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    cost_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS impulses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL CHECK(direction IN ('buy','sell')),
    target_code TEXT NOT NULL,
    target_name TEXT NOT NULL,
    emotion TEXT NOT NULL CHECK(emotion IN ('FOMO','恐慌','贪婪','冷静','其他')),
    reason TEXT DEFAULT '',
    cooldown_hours INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','cooling','completed','cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cooldowns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    impulse_id INTEGER NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    completed INTEGER DEFAULT 0,
    FOREIGN KEY(impulse_id) REFERENCES impulses(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    impulse_id INTEGER NOT NULL,
    final_decision TEXT CHECK(final_decision IN ('executed','abandoned','modified')),
    note TEXT DEFAULT '',
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(impulse_id) REFERENCES impulses(id)
);

CREATE TABLE IF NOT EXISTS trap_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections.

    Ensures the connection is properly closed after use.
    Enables row_factory for dict-like access.

    Yields:
        A sqlite3.Connection object with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database by creating all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    """Fetch all rows from a query as dictionaries.

    Args:
        sql: SQL query string.
        params: Query parameters tuple.

    Returns:
        List of dictionaries representing rows.
    """
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def fetch_one(sql: str, params: tuple = ()) -> Optional[dict]:
    """Fetch a single row from a query as a dictionary.

    Args:
        sql: SQL query string.
        params: Query parameters tuple.

    Returns:
        A dictionary representing the row, or None if not found.
    """
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple = ()) -> int:
    """Execute a write query and return affected row info.

    For INSERT, returns the last inserted row ID.
    For UPDATE/DELETE, returns the number of affected rows.

    Args:
        sql: SQL query string.
        params: Query parameters tuple.

    Returns:
        The row ID of the last inserted row, or the number of
        affected rows for other queries.
    """
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
