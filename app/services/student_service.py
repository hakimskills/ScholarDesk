# -*- coding: utf-8 -*-
"""
app/services/student_service.py

All SQL for the students table lives here. UI code should never
import sqlite3 or write SQL directly — it calls these functions and
works with Student objects.
"""

from typing import List, Optional

from app.database import get_connection
from app.models.student import Student


def get_all_students(search: str = "", class_name: str = "", payment_status: str = "") -> List[Student]:
    """Return students matching the optional filters, most recent first."""
    query = "SELECT * FROM students WHERE 1=1"
    params: list = []

    if search:
        query += """ AND (
            first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR
            guardian LIKE ? OR file_number LIKE ? OR code LIKE ?
        )"""
        like = f"%{search}%"
        params += [like, like, like, like, like, like]
    if class_name:
        query += " AND class_name = ?"
        params.append(class_name)
    if payment_status:
        query += " AND payment_status = ?"
        params.append(payment_status)

    query += " ORDER BY id DESC"
    rows = get_connection().execute(query, params).fetchall()
    return [Student.from_row(row) for row in rows]


def get_student(student_id: int) -> Optional[Student]:
    row = get_connection().execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    return Student.from_row(row) if row else None


def create_student(student: Student) -> Student:
    """
    Insert a new student. class_name is deliberately left as-is
    (empty by default) — students are added without a class and get
    assigned to one later via the edit dialog.
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO students (
            first_name, last_name, file_number, code, birth_date, birth_place,
            guardian, address, phone, guardian_phone, educational_institution,
            class_name, joined_at, payment_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student.first_name, student.last_name, student.file_number, student.code,
            student.birth_date, student.birth_place, student.guardian, student.address,
            student.phone, student.guardian_phone, student.educational_institution,
            student.class_name, student.joined_at, student.payment_status,
        ),
    )
    conn.commit()
    student.id = cursor.lastrowid
    return student


def update_student(student: Student) -> None:
    if student.id is None:
        raise ValueError("Cannot update a student that hasn't been saved yet (id is None)")
    conn = get_connection()
    conn.execute(
        """
        UPDATE students
        SET first_name = ?, last_name = ?, file_number = ?, code = ?, birth_date = ?,
            birth_place = ?, guardian = ?, address = ?, phone = ?, guardian_phone = ?,
            educational_institution = ?, class_name = ?, joined_at = ?, payment_status = ?
        WHERE id = ?
        """,
        (
            student.first_name, student.last_name, student.file_number, student.code,
            student.birth_date, student.birth_place, student.guardian, student.address,
            student.phone, student.guardian_phone, student.educational_institution,
            student.class_name, student.joined_at, student.payment_status, student.id,
        ),
    )
    conn.commit()


def assign_class(student_id: int, class_name: str) -> None:
    """Convenience helper for the "assign class later" flow."""
    conn = get_connection()
    conn.execute("UPDATE students SET class_name = ? WHERE id = ?", (class_name, student_id))
    conn.commit()


def delete_student(student_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()


def count_students() -> int:
    row = get_connection().execute("SELECT COUNT(*) AS c FROM students").fetchone()
    return row["c"]