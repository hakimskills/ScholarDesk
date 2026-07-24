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
        query += " AND (name LIKE ? OR phone LIKE ? OR guardian LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
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
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO students (name, class_name, guardian, phone, joined_at, payment_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (student.name, student.class_name, student.guardian, student.phone,
         student.joined_at, student.payment_status),
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
        SET name = ?, class_name = ?, guardian = ?, phone = ?, joined_at = ?, payment_status = ?
        WHERE id = ?
        """,
        (student.name, student.class_name, student.guardian, student.phone,
         student.joined_at, student.payment_status, student.id),
    )
    conn.commit()


def delete_student(student_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()


def count_students() -> int:
    row = get_connection().execute("SELECT COUNT(*) AS c FROM students").fetchone()
    return row["c"]


def seed_demo_data() -> None:
    """
    Populate the table with the placeholder rows the UI used to
    hardcode. Safe to call on every startup — it's a no-op once the
    table already has data. Call this once from main.py if you want
    to start with sample rows instead of an empty table.
    """
    if count_students() > 0:
        return
    demo = [
        Student("ياسين بلحاج", "السنة 3", "محمد بلحاج", "0551 23 45 67", "12/09/2025", "paid"),
        Student("مريم عبد الرحمان", "تحضيري", "سمير عبد الرحمان", "0662 34 56 78", "03/10/2025", "paid"),
        Student("عمر شريف", "السنة 2", "كريم شريف", "0770 45 67 89", "20/09/2025", "unpaid"),
        Student("لينا مرابط", "السنة 5", "فريد مرابط", "0554 56 78 90", "05/09/2025", "partial"),
        Student("آدم بوزيد", "السنة 1", "ياسمين بوزيد", "0661 67 89 01", "18/09/2025", "paid"),
        Student("نور الهدى قاسمي", "السنة 4", "عبد القادر قاسمي", "0772 78 90 12", "02/10/2025", "unpaid"),
        Student("إلياس حمدي", "السنة 3", "رشيد حمدي", "0553 89 01 23", "14/09/2025", "paid"),
        Student("سارة بن عيسى", "تحضيري", "نبيل بن عيسى", "0663 90 12 34", "27/09/2025", "partial"),
    ]
    for student in demo:
        create_student(student)