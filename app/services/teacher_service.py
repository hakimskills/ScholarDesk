# -*- coding: utf-8 -*-
"""
app/services/teacher_service.py

All SQL for the teachers table lives here. UI code should never
import sqlite3 or write SQL directly — it calls these functions and
works with Teacher objects. Mirrors app/services/student_service.py.
"""

from typing import List, Optional

from app.database import get_connection
from app.models.teacher import Teacher


def get_all_teachers(search: str = "", subject: str = "", gender: str = "") -> List[Teacher]:
    """Return teachers matching the optional filters, most recent first."""
    query = "SELECT * FROM teachers WHERE 1=1"
    params: list = []

    if search:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if gender:
        query += " AND gender = ?"
        params.append(gender)

    query += " ORDER BY id DESC"
    rows = get_connection().execute(query, params).fetchall()
    return [Teacher.from_row(row) for row in rows]


def get_teacher(teacher_id: int) -> Optional[Teacher]:
    row = get_connection().execute(
        "SELECT * FROM teachers WHERE id = ?", (teacher_id,)
    ).fetchone()
    return Teacher.from_row(row) if row else None


def create_teacher(teacher: Teacher) -> Teacher:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO teachers (
            first_name, last_name, gender, subject, birth_date, address, phone, joined_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            teacher.first_name, teacher.last_name, teacher.gender, teacher.subject,
            teacher.birth_date, teacher.address, teacher.phone, teacher.joined_at,
        ),
    )
    conn.commit()
    teacher.id = cursor.lastrowid
    return teacher


def update_teacher(teacher: Teacher) -> None:
    if teacher.id is None:
        raise ValueError("Cannot update a teacher that hasn't been saved yet (id is None)")
    conn = get_connection()
    conn.execute(
        """
        UPDATE teachers
        SET first_name = ?, last_name = ?, gender = ?, subject = ?, birth_date = ?,
            address = ?, phone = ?, joined_at = ?
        WHERE id = ?
        """,
        (
            teacher.first_name, teacher.last_name, teacher.gender, teacher.subject,
            teacher.birth_date, teacher.address, teacher.phone, teacher.joined_at, teacher.id,
        ),
    )
    conn.commit()


def delete_teacher(teacher_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()


def count_teachers() -> int:
    row = get_connection().execute("SELECT COUNT(*) AS c FROM teachers").fetchone()
    return row["c"]