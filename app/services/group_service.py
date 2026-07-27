# -*- coding: utf-8 -*-
"""
app/services/group_service.py

All SQL for the groups (فوج) table AND its many-to-many relationship
to students (group_students) lives here. UI code should never import
sqlite3 or write SQL directly.

Relationship rules enforced here (not by the database, since SQLite
CHECK constraints can't express "at most one row per group" across
tables easily for this shape — teacher_id is just a plain nullable
column on groups, which already gives us "one teacher per group" for
free; nothing stops the same teacher_id from appearing on many
groups, which is exactly "a teacher can teach many groups"):

- One teacher per group  -> groups.teacher_id (nullable FK, singular)
- A teacher can teach many groups -> no uniqueness constraint on
  teacher_id, so it's simply reused across rows.
- Many students per group, and a student can be in more than one
  group -> group_students junction table.
"""

from typing import List, Optional

from app.database import get_connection
from app.models.group import Group
from app.models.student import Student


def get_all_groups(search: str = "", level: str = "", subject: str = "", section: str = "", teacher_id: Optional[int] = None) -> List[Group]:
    """Return groups matching the optional filters, most recent first.

    level/subject are freeform text (no fixed list), so they're
    matched as substrings here rather than exact values. section
    comes from a small fixed dropdown (A-F...), so it's matched
    exactly.
    """
    query = "SELECT * FROM groups WHERE 1=1"
    params: list = []

    if search:
        query += " AND (level LIKE ? OR subject LIKE ? OR section LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
    if level:
        query += " AND level LIKE ?"
        params.append(f"%{level}%")
    if subject:
        query += " AND subject LIKE ?"
        params.append(f"%{subject}%")
    if section:
        query += " AND section = ?"
        params.append(section)
    if teacher_id is not None:
        query += " AND teacher_id = ?"
        params.append(teacher_id)

    query += " ORDER BY id DESC"
    rows = get_connection().execute(query, params).fetchall()
    return [Group.from_row(row) for row in rows]


def get_group(group_id: int) -> Optional[Group]:
    row = get_connection().execute(
        "SELECT * FROM groups WHERE id = ?", (group_id,)
    ).fetchone()
    return Group.from_row(row) if row else None


def create_group(group: Group, student_ids: Optional[List[int]] = None) -> Group:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO groups (
            level, subject, section, sessions_per_round, duration_hours, teacher_id,
            student_amount, teacher_pay_by_percentage, teacher_student_amount, branch, note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            group.level, group.subject, group.section, group.sessions_per_round,
            group.duration_hours, group.teacher_id, group.student_amount,
            int(group.teacher_pay_by_percentage), group.teacher_student_amount,
            group.branch, group.note,
        ),
    )
    conn.commit()
    group.id = cursor.lastrowid
    set_group_students(group.id, student_ids or [])
    return group


def update_group(group: Group, student_ids: Optional[List[int]] = None) -> None:
    if group.id is None:
        raise ValueError("Cannot update a group that hasn't been saved yet (id is None)")
    conn = get_connection()
    conn.execute(
        """
        UPDATE groups
        SET level = ?, subject = ?, section = ?, sessions_per_round = ?, duration_hours = ?,
            teacher_id = ?, student_amount = ?, teacher_pay_by_percentage = ?,
            teacher_student_amount = ?, branch = ?, note = ?
        WHERE id = ?
        """,
        (
            group.level, group.subject, group.section, group.sessions_per_round,
            group.duration_hours, group.teacher_id, group.student_amount,
            int(group.teacher_pay_by_percentage), group.teacher_student_amount,
            group.branch, group.note, group.id,
        ),
    )
    conn.commit()
    if student_ids is not None:
        set_group_students(group.id, student_ids)


def delete_group(group_id: int) -> None:
    """Deletes the group; its group_students rows go with it (ON DELETE CASCADE)."""
    conn = get_connection()
    conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    conn.commit()


def count_groups() -> int:
    row = get_connection().execute("SELECT COUNT(*) AS c FROM groups").fetchone()
    return row["c"]


# ---------------------------------------------------------------------- #
# Many-to-many: students <-> groups
# ---------------------------------------------------------------------- #

def get_group_student_ids(group_id: int) -> List[int]:
    rows = get_connection().execute(
        "SELECT student_id FROM group_students WHERE group_id = ?", (group_id,)
    ).fetchall()
    return [row["student_id"] for row in rows]


def get_students_for_group(group_id: int) -> List[Student]:
    rows = get_connection().execute(
        """
        SELECT students.* FROM students
        INNER JOIN group_students ON group_students.student_id = students.id
        WHERE group_students.group_id = ?
        ORDER BY students.id DESC
        """,
        (group_id,),
    ).fetchall()
    return [Student.from_row(row) for row in rows]


def count_students_in_group(group_id: int) -> int:
    row = get_connection().execute(
        "SELECT COUNT(*) AS c FROM group_students WHERE group_id = ?", (group_id,)
    ).fetchone()
    return row["c"]


def set_group_students(group_id: int, student_ids: List[int]) -> None:
    """Replace a group's entire student roster with the given list."""
    conn = get_connection()
    conn.execute("DELETE FROM group_students WHERE group_id = ?", (group_id,))
    conn.executemany(
        "INSERT INTO group_students (group_id, student_id) VALUES (?, ?)",
        [(group_id, student_id) for student_id in student_ids],
    )
    conn.commit()


def get_groups_for_teacher(teacher_id: int) -> List[Group]:
    """All groups a given teacher teaches — a teacher can teach many."""
    return get_all_groups(teacher_id=teacher_id)