# -*- coding: utf-8 -*-
"""
app/models/teacher.py

Plain data holder for one teacher. No Qt, no SQL — app/services
converts sqlite3.Row objects into these and back when talking to
the database. Mirrors app/models/student.py's shape/conventions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Teacher:
    first_name: str
    last_name: str
    phone: str
    joined_at: str

    gender: str = ""
    subject: str = ""
    birth_date: str = ""
    address: str = ""

    id: Optional[int] = None

    @property
    def full_name(self) -> str:
        """Display name as "اللقب الإسم" (last name first, Arabic convention)."""
        return " ".join(part for part in (self.last_name, self.first_name) if part).strip()

    @classmethod
    def from_row(cls, row) -> "Teacher":
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone=row["phone"],
            joined_at=row["joined_at"],
            gender=row["gender"],
            subject=row["subject"],
            birth_date=row["birth_date"],
            address=row["address"],
        )