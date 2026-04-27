from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('member', 'admin'))
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection(db_path)) as connection:
        connection.executescript(SCHEMA)
        connection.commit()


def upsert_user(db_path: str, username: str, password_hash: str, role: str) -> None:
    with closing(get_connection(db_path)) as connection:
        connection.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password_hash = excluded.password_hash,
                role = excluded.role
            """,
            (username, password_hash, role),
        )
        connection.commit()


def get_user_by_username(db_path: str, username: str):
    with closing(get_connection(db_path)) as connection:
        return connection.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def get_user_by_id(db_path: str, user_id: int):
    with closing(get_connection(db_path)) as connection:
        return connection.execute(
            "SELECT id, username, password_hash, role FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def add_comment(db_path: str, username: str, message: str) -> None:
    with closing(get_connection(db_path)) as connection:
        connection.execute(
            "INSERT INTO comments (username, message) VALUES (?, ?)",
            (username, message),
        )
        connection.commit()


def list_comments(db_path: str):
    with closing(get_connection(db_path)) as connection:
        return connection.execute(
            """
            SELECT id, username, message, created_at
            FROM comments
            ORDER BY id DESC
            """
        ).fetchall()
