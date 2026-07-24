# -*- coding: utf-8 -*-
"""
app/models/student.py

Plain data holder for one student. No Qt, no SQL — app/services
converts sqlite3.Row objects into these and back when talking to
the database.

class_name is intentionally optional here: students are created
without a class and get assigned to one later (see student_form.py,
which only shows the class field in edit mode).
"""

from dataclasses import dataclass
from typing import Optional

# Keep this in sync with the CHECK constraint in app/database.py
PAYMENT_STATUSES = ("paid", "unpaid")

# Sentinel used everywhere (model, service, UI) for "not assigned yet".
UNASSIGNED_CLASS = ""


@dataclass
class Student:
    # Identity / registration info (collected when the student is added)
    first_name: str
    last_name: str
    guardian: str
    phone: str
    joined_at: str

    # Extra registration details (from the reference form)
    file_number: str = ""
    code: str = ""
    birth_date: str = ""
    birth_place: str = ""
    address: str = ""
    guardian_phone: str = ""
    educational_institution: str = ""

    # Assigned later, not at creation time
    class_name: str = UNASSIGNED_CLASS

    payment_status: str = "unpaid"
    id: Optional[int] = None

    @property
    def full_name(self) -> str:
        """Display name as "اللقب الإسم" (last name first, Arabic convention)."""
        return " ".join(part for part in (self.last_name, self.first_name) if part).strip()

    @property
    def has_class(self) -> bool:
        return bool(self.class_name)

    @classmethod
    def from_row(cls, row) -> "Student":
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            guardian=row["guardian"],
            phone=row["phone"],
            joined_at=row["joined_at"],
            file_number=row["file_number"],
            code=row["code"],
            birth_date=row["birth_date"],
            birth_place=row["birth_place"],
            address=row["address"],
            guardian_phone=row["guardian_phone"],
            educational_institution=row["educational_institution"],
            class_name=row["class_name"],
            payment_status=row["payment_status"],
        )