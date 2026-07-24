# -*- coding: utf-8 -*-
"""
app/models/student.py

Plain data holder for one student. No Qt, no SQL — app/services
converts sqlite3.Row objects into these and back when talking to
the database.
"""

from dataclasses import dataclass
from typing import Optional

# Keep this in sync with the CHECK constraint in app/database.py
PAYMENT_STATUSES = ("paid", "unpaid")


@dataclass
class Student:
    name: str
    class_name: str
    guardian: str
    phone: str
    joined_at: str
    payment_status: str = "unpaid"
    id: Optional[int] = None

    @classmethod
    def from_row(cls, row) -> "Student":
        return cls(
            id=row["id"],
            name=row["name"],
            class_name=row["class_name"],
            guardian=row["guardian"],
            phone=row["phone"],
            joined_at=row["joined_at"],
            payment_status=row["payment_status"],
        )