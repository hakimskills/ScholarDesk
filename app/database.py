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

_CREATE_STUDENTS_TABLE = """
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

# Columns added after the original release. Each is TEXT NOT NULL
# DEFAULT '' so existing rows (and the "assign class later" flow,
# where class_name starts empty) stay valid without extra checks.
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
    "class_name",
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
    Create tables if they don't exist yet, and bring an older
    database up to the current schema. Safe to call on every
    startup — every step below is a no-op once the schema is already
    current.
    """
    conn = get_connection()
    conn.executescript(_CREATE_STUDENTS_TABLE)
    conn.commit()

    _rebuild_if_legacy_name_column(conn)
    _migrate_new_columns(conn)


def _existing_columns(conn: sqlite3.Connection) -> set:
    return {row["name"] for row in conn.execute("PRAGMA table_info(students)")}


def _rebuild_if_legacy_name_column(conn: sqlite3.Connection):
    """
    The very first schema stored a single NOT NULL 'name' column.
    Simply adding new columns alongside it (via ALTER TABLE) leaves
    that old constraint in place, which then breaks every insert
    that doesn't set 'name' — exactly what the new create/update
    code does. So instead of patching around it, rebuild the table
    from scratch on the new schema and carry every row's data over,
    folding the legacy 'name' into 'last_name' when needed. No-op
    once the 'name' column is gone.
    """
    existing = _existing_columns(conn)
    if "name" not in existing:
        return

    old_rows = conn.execute("SELECT * FROM students").fetchall()

    conn.execute("ALTER TABLE students RENAME TO students_legacy")
    conn.executescript(_CREATE_STUDENTS_TABLE)

    for row in old_rows:
        keys = row.keys()

        def get(column, default=""):
            return row[column] if column in keys and row[column] is not None else default

        first_name = get("first_name")
        last_name = get("last_name")
        if not first_name and not last_name:
            # Nothing split yet for this row — fall back to the old
            # single-field name so the student keeps a readable name.
            last_name = get("name")

        payment_status = get("payment_status", "unpaid")
        if payment_status not in ("paid", "unpaid"):
            # Safety net only, so the CHECK constraint on the rebuilt
            # table can't reject a row during migration.
            payment_status = "unpaid"

        conn.execute(
            """
            INSERT INTO students (
                id, first_name, last_name, file_number, code, birth_date, birth_place,
                guardian, address, phone, guardian_phone, educational_institution,
                class_name, joined_at, payment_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                get("id"), first_name, last_name, get("file_number"), get("code"),
                get("birth_date"), get("birth_place"), get("guardian"), get("address"),
                get("phone"), get("guardian_phone"), get("educational_institution"),
                get("class_name"), get("joined_at"), payment_status,
            ),
        )

    conn.execute("DROP TABLE students_legacy")
    conn.commit()


def _migrate_new_columns(conn: sqlite3.Connection):
    """
    Add any column introduced after the table was first created, for
    a database that already dropped 'name' (via an earlier version
    of this migration) but predates one of the newer fields. No-op
    once the schema already has them all.
    """
    existing = _existing_columns(conn)
    for column in _NEW_TEXT_COLUMNS:
        if column not in existing:
            conn.execute(f"ALTER TABLE students ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
    conn.commit()


def close_connection():
    """Close the shared connection. Mostly useful for tests."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None