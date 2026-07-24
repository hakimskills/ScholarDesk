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
    is in place.
    """
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            class_name     TEXT NOT NULL,
            guardian       TEXT NOT NULL,
            phone          TEXT NOT NULL,
            joined_at      TEXT NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'unpaid'
                CHECK (payment_status IN ('paid', 'unpaid'))
        );
        """
    )
    conn.commit()
    _migrate_legacy_partial_status(conn)


def _migrate_legacy_partial_status(conn: sqlite3.Connection):
    """
    Earlier versions of this table allowed a third 'partial' status.
    Collapse any leftover rows from that period into 'unpaid' so old
    test data doesn't linger with a status the UI no longer shows.
    No-op if none exist.
    """
    conn.execute("UPDATE students SET payment_status = 'unpaid' WHERE payment_status = 'partial'")
    conn.commit()


def close_connection():
    """Close the shared connection. Mostly useful for tests."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None