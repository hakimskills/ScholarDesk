# -*- coding: utf-8 -*-
"""
app/ui/group_students_dialog.py

"إدارة التلاميذ" — add/remove a group's students, opened by
right-clicking a row in app/ui/groups.py. This is deliberately
separate from app/ui/group_form.py: creating or editing a group only
ever touches the group's own fields, and membership is edited here
instead, once the group already exists.

Shows every student in a search-filterable, checkable list (checked
= currently a member of this group). Saving replaces the group's
whole roster in one call via group_service.set_group_students, which
already does the diff internally (DELETE + re-INSERT), so this
dialog just needs to hand over the final selected id list.

Styled with the same formDialog/formCard building blocks used by
app/ui/group_form.py so it reads as part of the same app rather than
a bolted-on picker.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit,
    QListWidget, QListWidgetItem,
)
from PySide6.QtCore import Qt

from app.models.group import Group
from app.services import group_service, student_service
from app.common import make_label, make_button


def _make_search_box(placeholder: str) -> QLineEdit:
    box = QLineEdit(objectName="formInput")
    box.setAlignment(Qt.AlignRight)
    box.setPlaceholderText(placeholder)
    return box


class GroupStudentsDialog(QDialog):
    """Add/remove students for one existing group."""

    def __init__(self, group: Group, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._group = group
        self.setWindowTitle("إدارة تلاميذ الفوج")
        self.setMinimumWidth(480)

        self._build_ui()
        self._load_students()
        self._fit_to_screen()

    # ------------------------------------------------------------------ #
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 16)
        outer.setSpacing(14)

        header = QVBoxLayout()
        header.setSpacing(2)
        header.addWidget(make_label("إدارة تلاميذ الفوج", "formTitle", align=Qt.AlignRight))
        header.addWidget(make_label(
            self._group.display_name or "—", "formSubtitle", align=Qt.AlignRight,
        ))
        outer.addLayout(header)

        card = QFrame(objectName="formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(12)

        self.search_input = _make_search_box("🔍  ابحث عن تلميذ بالاسم لإضافته أو حذفه...")
        self.search_input.textChanged.connect(self._filter_list)
        card_layout.addWidget(self.search_input)

        self.student_list = QListWidget()
        self.student_list.setObjectName("studentPickList")
        self.student_list.setLayoutDirection(Qt.RightToLeft)
        self.student_list.setMinimumHeight(320)
        self.student_list.itemChanged.connect(self._update_count_label)
        card_layout.addWidget(self.student_list, 1)

        divider = QFrame(objectName="formHeaderSeparator")
        divider.setFrameShape(QFrame.HLine)
        card_layout.addWidget(divider)

        footer_row = QHBoxLayout()
        self.count_label = make_label(
            "لم يتم اختيار أي تلميذ بعد",
            style="color: #6B7189; font-size: 11.5px;",
            align=Qt.AlignRight,
        )
        footer_row.addWidget(self.count_label, 1)
        footer_row.addWidget(make_button("تحديد الكل", "outlineButton", on_click=self._select_all))
        footer_row.addWidget(make_button("إلغاء التحديد", "outlineButton", on_click=self._deselect_all))
        card_layout.addLayout(footer_row)

        outer.addWidget(card, 1)
        outer.addLayout(self._build_buttons_row())

    def _fit_to_screen(self):
        screen = self.screen() or (self.parent().screen() if self.parent() else None)
        if screen is None:
            return
        available = screen.availableGeometry()
        max_height = max(420, int(available.height() * 0.85))
        self.resize(self.width(), min(self.sizeHint().height(), max_height))
        self.setMaximumHeight(max_height)

    def _build_buttons_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch(1)
        row.addWidget(make_button("إلغاء", "outlineButton", on_click=self.reject))
        row.addWidget(make_button("حفظ", "primaryButton", on_click=self._on_save))
        return row

    # ------------------------------------------------------------------ #
    def _load_students(self):
        member_ids = set(group_service.get_group_student_ids(self._group.id)) if self._group.id else set()
        self.student_list.blockSignals(True)
        for student in student_service.get_all_students():
            item = QListWidgetItem(student.full_name)
            item.setData(Qt.UserRole, student.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if student.id in member_ids else Qt.Unchecked)
            self.student_list.addItem(item)
        self.student_list.blockSignals(False)
        self._update_count_label()

    def _filter_list(self, text: str):
        text = text.strip()
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            item.setHidden(bool(text) and text not in item.text())

    def _select_all(self):
        self._set_visible_checked(Qt.Checked)

    def _deselect_all(self):
        self._set_visible_checked(Qt.Unchecked)

    def _set_visible_checked(self, state):
        self.student_list.blockSignals(True)
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            if not item.isHidden():
                item.setCheckState(state)
        self.student_list.blockSignals(False)
        self._update_count_label()

    def _update_count_label(self, *_):
        count = sum(
            1 for row in range(self.student_list.count())
            if self.student_list.item(row).checkState() == Qt.Checked
        )
        self.count_label.setText(f"{count} تلميذ مختار" if count else "لم يتم اختيار أي تلميذ بعد")

    def _selected_student_ids(self):
        return [
            self.student_list.item(row).data(Qt.UserRole)
            for row in range(self.student_list.count())
            if self.student_list.item(row).checkState() == Qt.Checked
        ]

    def _on_save(self):
        group_service.set_group_students(self._group.id, self._selected_student_ids())
        self.accept()