# -*- coding: utf-8 -*-
"""
app/database.py

Owns the single SQLite connection and the schema. Nothing else in
the app should import sqlite3 directly — services use
`get_connection()`, and `init_db()` is called once at startup
(see main.py) before any service touches the database.
"""

import os
import sqlite3
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
DB_PATH = os.path.join(DATA_DIR, "school.db")

_connection: Optional[sqlite3.Connection] = None

# Columns added after the original release. Each is TEXT NOT NULL
# DEFAULT '' so existing rows (and the "assign class later" flow,
# where class_name starts empty) stay valid without extra checks.
# NOTE: name here is the *new* schema; "name" (old single-field name)
# is handled separately by _migrate_legacy_name_column below.
_NEW_TEXT_COLUMNS = [
    "first_name",
    "last_name",
    "file_number",
    "code",
    "birth_date",
    "birth_place",
    "address",
    "guardian_phone",
    "educational_institution",
]


def get_connection() -> sqlite3.Connection:
    """Return the shared SQLite connection, opening it on first use."""
    global _connection
    if _connection is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


def init_db():
    """
    Create tables if they don't exist yet. Safe to call on every
    startup — CREATE TABLE IF NOT EXISTS is a no-op once the schema
    is in place, and the migration helpers below only add what's
    missing.
    """
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name              TEXT NOT NULL DEFAULT '',
            last_name               TEXT NOT NULL DEFAULT '',
            file_number             TEXT NOT NULL DEFAULT '',
            code                    TEXT NOT NULL DEFAULT '',
            birth_date              TEXT NOT NULL DEFAULT '',
            birth_place             TEXT NOT NULL DEFAULT '',
            guardian                TEXT NOT NULL DEFAULT '',
            address                 TEXT NOT NULL DEFAULT '',
            phone                   TEXT NOT NULL DEFAULT '',
            guardian_phone          TEXT NOT NULL DEFAULT '',
            educational_institution TEXT NOT NULL DEFAULT '',
            class_name              TEXT NOT NULL DEFAULT '',
            joined_at               TEXT NOT NULL,
            payment_status          TEXT NOT NULL DEFAULT 'unpaid'
                CHECK (payment_status IN ('paid', 'unpaid'))
        );
        """
    )
    conn.commit()
    _migrate_new_columns(conn)
    _migrate_legacy_name_column(conn)


def _existing_columns(conn: sqlite3.Connection) -> set:
    return {row["name"] for row in conn.execute("PRAGMA table_info(students)")}


def _migrate_new_columns(conn: sqlite3.Connection):
    """
    Add any column introduced after the table was first created (e.g.
    on a database from an older version of the app). No-op once the
    schema already has them.
    """
    existing = _existing_columns(conn)
    for column in _NEW_TEXT_COLUMNS:
        if column not in existing:
            conn.execute(f"ALTER TABLE students ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
    if "class_name" not in existing:
        conn.execute("ALTER TABLE students ADD COLUMN class_name TEXT NOT NULL DEFAULT ''")
    conn.commit()


def _migrate_legacy_name_column(conn: sqlite3.Connection):
    """
    The very first schema stored a single 'name' column. If it's
    still around, fold it into last_name for any row that hasn't
    been split yet, so existing students keep a readable name after
    upgrading. Safe/no-op once there's nothing left to migrate.
    """
    existing = _existing_columns(conn)
    if "name" not in existing:
        return
    conn.execute(
        """
        UPDATE students
        SET last_name = name
        WHERE (last_name IS NULL OR last_name = '')
          AND (first_name IS NULL OR first_name = '')
          AND name IS NOT NULL AND name != ''
        """
    )
    conn.commit()


def close_connection():
    """Close the shared connection. Mostly useful for tests."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None