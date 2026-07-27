# -*- coding: utf-8 -*-
"""
app/ui/group_details_dialog.py

Read-only "تفاصيل الفوج" popup, opened by double-clicking a group's
row in app/ui/groups.py. The table only has room for a handful of
summary columns, so this shows every field on the group in one
place — its own info, the teacher/payment info, and its full student
roster — with a visible divider line between each block so it's
obvious at a glance where one group of facts ends and the next
begins (the same formHeaderSeparator line app/ui/group_form.py uses
between its sections).

Pure display: nothing here writes to the database. Editing the
group's fields is still done through app/ui/group_form.py, and
editing its roster through app/ui/group_students_dialog.py.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QListWidget, QListWidgetItem, QScrollArea,
)
from PySide6.QtCore import Qt

from app.models.group import Group
from app.services import group_service, teacher_service
from app.common import make_label, make_button

_NO_TEACHER_LABEL = "بدون أستاذ"


def _display_field(label_text: str, value: str) -> QVBoxLayout:
    """Label above its value — read-only counterpart of group_form's
    _field_box, so the layout rhythm matches the add/edit form."""
    box = QVBoxLayout()
    box.setSpacing(4)
    box.addWidget(make_label(label_text, "formFieldLabel", align=Qt.AlignRight))
    box.addWidget(make_label(
        value or "—", align=Qt.AlignRight,
        style="font-size: 13px; font-weight: 600; color: #1B2140;",
    ))
    return box


class GroupDetailsDialog(QDialog):
    """Read-only detail view for one group, opened via double-click."""

    def __init__(self, group: Group, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle("تفاصيل الفوج")
        self.setMinimumWidth(560)
        self._group = group

        self._build_ui()
        self._fit_to_screen()

    # ------------------------------------------------------------------ #
    def _separator(self) -> QFrame:
        line = QFrame(objectName="formHeaderSeparator")
        line.setFrameShape(QFrame.HLine)
        return line

    def _section_title(self, text: str):
        return make_label(text, "formSectionTitle", align=Qt.AlignRight)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 16)
        outer.setSpacing(14)

        header = QVBoxLayout()
        header.setSpacing(2)
        header.addWidget(make_label("تفاصيل الفوج", "formTitle", align=Qt.AlignRight))
        header.addWidget(make_label(self._group.display_name or "—", "formSubtitle", align=Qt.AlignRight))
        outer.addLayout(header)

        card = QFrame(objectName="formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(18)

        card_layout.addLayout(self._build_group_info())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_teacher_payment_info())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_students_info())
        if self._group.note:
            card_layout.addWidget(self._separator())
            card_layout.addLayout(self._build_notes_info())

        scroll = QScrollArea()
        scroll.setObjectName("formScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setLayoutDirection(Qt.RightToLeft)
        scroll.setWidget(card)
        outer.addWidget(scroll, 1)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(make_button("إغلاق", "primaryButton", on_click=self.accept))
        outer.addLayout(row)

    def _fit_to_screen(self):
        screen = self.screen() or (self.parent().screen() if self.parent() else None)
        if screen is None:
            return
        available = screen.availableGeometry()
        max_height = max(480, int(available.height() * 0.9))
        self.resize(self.width(), min(self.sizeHint().height(), max_height))
        self.setMaximumHeight(max_height)

    # ------------------------------------------------------------------ #
    # Sections
    # ------------------------------------------------------------------ #
    def _build_group_info(self) -> QVBoxLayout:
        g = self._group
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("معلومات الفوج"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)
        grid.addLayout(_display_field("المستوى", g.level), 0, 0)
        grid.addLayout(_display_field("المادة", g.subject), 0, 1)
        grid.addLayout(_display_field("الفوج", g.section), 1, 0)
        grid.addLayout(_display_field("عدد الحصص/الجولة", str(g.sessions_per_round)), 1, 1)
        grid.addLayout(_display_field("المدة (سا)", f"{g.duration_hours:g} سا"), 2, 0)
        grid.addLayout(_display_field("الفرع", g.branch), 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        section.addLayout(grid)
        return section

    def _build_teacher_payment_info(self) -> QVBoxLayout:
        g = self._group
        teacher = teacher_service.get_teacher(g.teacher_id) if g.teacher_id else None
        teacher_label = teacher.full_name if teacher else _NO_TEACHER_LABEL
        pct = g.percentage

        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("الأستاذ والمدفوعات"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)
        grid.addLayout(_display_field("الأستاذ", teacher_label), 0, 0)
        grid.addLayout(_display_field("مبلغ التلميذ", f"{g.student_amount:g} دج"), 0, 1)
        grid.addLayout(_display_field(
            "مدفوعات بالنسبة المئوية", "نعم" if g.teacher_pay_by_percentage else "لا",
        ), 1, 0)
        grid.addLayout(_display_field("مبلغ الأستاذ/تلميذ", f"{g.teacher_student_amount:g} دج"), 1, 1)
        grid.addLayout(_display_field("النسبة", f"{pct}%" if pct is not None else "—"), 2, 0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        section.addLayout(grid)
        return section

    def _build_students_info(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(10)
        students = group_service.get_students_for_group(self._group.id) if self._group.id else []
        section.addWidget(self._section_title(f"التلاميذ ({len(students)})"))

        if not students:
            section.addWidget(make_label(
                "لا يوجد تلاميذ في هذا الفوج بعد. انقر بزر الفأرة الأيمن على الفوج في الجدول لإضافة تلاميذ.",
                align=Qt.AlignRight, style="color: #6B7189; font-size: 12px;",
            ))
            return section

        student_list = QListWidget()
        student_list.setLayoutDirection(Qt.RightToLeft)
        student_list.setMaximumHeight(160)
        student_list.setFocusPolicy(Qt.NoFocus)
        for student in students:
            student_list.addItem(QListWidgetItem(student.full_name))
        section.addWidget(student_list)
        return section

    def _build_notes_info(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(10)
        section.addWidget(self._section_title("ملاحظات"))
        section.addWidget(make_label(
            self._group.note, align=Qt.AlignRight, style="font-size: 12.5px; color: #1B2140;",
        ))
        return section