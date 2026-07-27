# -*- coding: utf-8 -*-
"""
app/models/group.py

Plain data holder for one فوج (class/group). No Qt, no SQL —
app/services converts sqlite3.Row objects into these and back when
talking to the database.

Relationships:
- teacher_id: at most ONE teacher per group (a teacher can still
  teach many groups — nothing here limits that; see
  app/services/group_service.py).
- students: MANY students per group, stored in a separate
  group_students junction table and handled by
  app/services/group_service.py (get_group_student_ids /
  set_group_students) — not a field on this dataclass, since it's a
  relationship, not a scalar column.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Group:
    level: str = ""                          # المستوى — free text, e.g. "3 ابتدائي"
    subject: str = ""                        # المادة — free text, e.g. "رياضيات"
    section: str = ""                        # الفوج — fixed letter, e.g. "A"
    sessions_per_round: int = 0              # عدد الحصص/الجولة
    duration_hours: float = 0.0              # المدة (سا)
    teacher_id: Optional[int] = None         # الأستاذ — one teacher per group
    student_amount: float = 0.0              # مبلغ التلميذ
    teacher_pay_by_percentage: bool = False  # مدفوعات الأستاذ بالنسبة المئوية
    teacher_student_amount: float = 0.0      # مبلغ الأستاذ/تلميذ
    branch: str = ""                         # الفرع
    note: str = ""                           # الملاحظة
    id: Optional[int] = None

    @property
    def display_name(self) -> str:
        """The class's own name: المستوى + المادة + الفوج, in that
        order — e.g. "3 ابتدائي رياضيات A". Not stored separately;
        always derived from the three parts so it can never drift
        out of sync with them."""
        return " ".join(part for part in (self.level, self.subject, self.section) if part).strip()

    @property
    def percentage(self) -> Optional[float]:
        """النسبة = مبلغ الأستاذ/تلميذ ÷ مبلغ التلميذ × 100, when both are set."""
        if self.student_amount and self.teacher_student_amount:
            return round((self.teacher_student_amount / self.student_amount) * 100, 1)
        return None

    @classmethod
    def from_row(cls, row) -> "Group":
        return cls(
            id=row["id"],
            level=row["level"],
            subject=row["subject"],
            section=row["section"],
            sessions_per_round=row["sessions_per_round"],
            duration_hours=row["duration_hours"],
            teacher_id=row["teacher_id"],
            student_amount=row["student_amount"],
            teacher_pay_by_percentage=bool(row["teacher_pay_by_percentage"]),
            teacher_student_amount=row["teacher_student_amount"],
            branch=row["branch"],
            note=row["note"],
        )