# -*- coding: utf-8 -*-
"""
app/ui/group_students_dialog.py

"إدارة التلاميذ" — add/remove a group's students, opened by
right-clicking (or the ✏-adjacent action) a row in app/ui/groups.py.
Deliberately separate from app/ui/group_form.py: creating or editing
a group only ever touches the group's own fields; membership is
edited here instead, once the group already exists.

Two tabs, like a browser, instead of one combined checklist:
- "إضافة تلاميذ"  — every student NOT already in this group, with a
  search box and a "إضافة المحدد" button.
- "تلاميذ الفوج"  — every student already IN this group, with its
  own search box, a "حذف المحدد" button for multi-select removal,
  and a right-click "🗑 حذف تلميذ" action for removing just one.

Every add/remove is written to the database immediately (via
group_service.add_students_to_group / remove_students_from_group) —
there's no separate "save" step for membership, so both tabs refresh
each other right away and the dialog only needs a single "إغلاق"
button.

Styled with the same formDialog/formCard building blocks used by
app/ui/group_form.py so it reads as part of the same app rather than
a bolted-on picker.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QTabWidget,
    QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QMenu,
)
from PySide6.QtCore import Qt

from app.models.group import Group
from app.services import group_service
from app.common import make_label, make_button


def _make_search_box(placeholder: str) -> QLineEdit:
    box = QLineEdit(objectName="formInput")
    box.setLayoutDirection(Qt.RightToLeft)
    box.setAlignment(Qt.AlignRight)
    box.setPlaceholderText(placeholder)
    return box


def _make_pick_list() -> QListWidget:
    list_widget = QListWidget()
    list_widget.setObjectName("studentPickList")
    list_widget.setLayoutDirection(Qt.RightToLeft)
    list_widget.setMinimumHeight(280)
    # Row selection isn't used for anything here — only the checkbox
    # matters — and Qt's default selection highlight was covering the
    # name text in a color that made it unreadable. Turning it off
    # entirely fixes that; the checkbox still toggles fine on click.
    list_widget.setSelectionMode(QAbstractItemView.NoSelection)
    list_widget.setFocusPolicy(Qt.NoFocus)
    return list_widget


class GroupStudentsDialog(QDialog):
    """Add/remove students for one existing group."""

    def __init__(self, group: Group, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._group = group
        self.setWindowTitle("إدارة تلاميذ الفوج")
        self.setMinimumWidth(500)

        self._build_ui()
        self._reload_add_tab()
        self._reload_members_tab()
        self._fit_to_screen()

    # ------------------------------------------------------------------ #
    # Layout
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
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        self.tabs.addTab(self._build_add_tab(), "إضافة تلاميذ")
        self.tabs.addTab(self._build_members_tab(), "تلاميذ الفوج")
        card_layout.addWidget(self.tabs)

        outer.addWidget(card, 1)
        outer.addLayout(self._build_buttons_row())

    def _fit_to_screen(self):
        screen = self.screen() or (self.parent().screen() if self.parent() else None)
        if screen is None:
            return
        available = screen.availableGeometry()
        max_height = max(460, int(available.height() * 0.85))
        self.resize(self.width(), min(self.sizeHint().height(), max_height))
        self.setMaximumHeight(max_height)

    def _build_buttons_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch(1)
        row.addWidget(make_button("إغلاق", "primaryButton", on_click=self.accept))
        return row

    # ------------------------------------------------------------------ #
    # Tab 1 — إضافة تلاميذ (students NOT in the group yet)
    # ------------------------------------------------------------------ #
    def _build_add_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 14, 4, 4)
        layout.setSpacing(12)

        self.add_search_input = _make_search_box("🔍  ابحث عن تلميذ لإضافته...")
        self.add_search_input.textChanged.connect(lambda text: self._filter_list(self.add_list, text))
        layout.addWidget(self.add_search_input)

        self.add_list = _make_pick_list()
        layout.addWidget(self.add_list, 1)

        footer = QHBoxLayout()
        self.add_count_label = make_label("", style="color: #6B7189; font-size: 11.5px;", align=Qt.AlignRight)
        footer.addWidget(self.add_count_label, 1)
        footer.addWidget(make_button("إضافة المحدد", "primaryButton", on_click=self._add_selected))
        layout.addLayout(footer)

        return tab

    def _reload_add_tab(self):
        self.add_list.clear()
        for student in group_service.get_students_not_in_group(self._group.id):
            item = QListWidgetItem(student.full_name)
            item.setData(Qt.UserRole, student.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.add_list.addItem(item)
        self.add_search_input.clear()
        self._update_add_count_label()

    def _update_add_count_label(self, *_):
        total = self.add_list.count()
        self.add_count_label.setText(
            f"{total} تلميذ متاح للإضافة" if total else "كل التلاميذ منضمّون لهذا الفوج بالفعل"
        )

    def _add_selected(self):
        selected_ids = self._checked_ids(self.add_list)
        if not selected_ids:
            return
        group_service.add_students_to_group(self._group.id, selected_ids)
        self._reload_add_tab()
        self._reload_members_tab()

    # ------------------------------------------------------------------ #
    # Tab 2 — تلاميذ الفوج (students already in the group)
    # ------------------------------------------------------------------ #
    def _build_members_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 14, 4, 4)
        layout.setSpacing(12)

        self.members_search_input = _make_search_box("🔍  ابحث عن تلميذ لحذفه...")
        self.members_search_input.textChanged.connect(lambda text: self._filter_list(self.members_list, text))
        layout.addWidget(self.members_search_input)

        self.members_list = _make_pick_list()
        self.members_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.members_list.customContextMenuRequested.connect(self._on_members_context_menu)
        layout.addWidget(self.members_list, 1)

        footer = QHBoxLayout()
        self.members_count_label = make_label("", style="color: #6B7189; font-size: 11.5px;", align=Qt.AlignRight)
        footer.addWidget(self.members_count_label, 1)
        footer.addWidget(make_button("حذف المحدد", "outlineButton", on_click=self._remove_selected))
        layout.addLayout(footer)

        return tab

    def _reload_members_tab(self):
        self.members_list.clear()
        for student in group_service.get_students_for_group(self._group.id):
            item = QListWidgetItem(student.full_name)
            item.setData(Qt.UserRole, student.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.members_list.addItem(item)
        self.members_search_input.clear()
        self._update_members_count_label()

    def _update_members_count_label(self, *_):
        total = self.members_list.count()
        self.members_count_label.setText(
            f"{total} تلميذ في هذا الفوج" if total else "لا يوجد تلاميذ في هذا الفوج بعد"
        )

    def _remove_selected(self):
        selected_ids = self._checked_ids(self.members_list)
        if not selected_ids:
            return
        group_service.remove_students_from_group(self._group.id, selected_ids)
        self._reload_members_tab()
        self._reload_add_tab()

    def _on_members_context_menu(self, pos):
        item = self.members_list.itemAt(pos)
        if item is None:
            return
        student_id = item.data(Qt.UserRole)

        menu = QMenu(self)
        menu.setLayoutDirection(Qt.RightToLeft)
        menu.addAction("🗑  حذف تلميذ", lambda: self._remove_one(student_id))
        menu.exec(self.members_list.viewport().mapToGlobal(pos))

    def _remove_one(self, student_id: int):
        group_service.remove_students_from_group(self._group.id, [student_id])
        self._reload_members_tab()
        self._reload_add_tab()

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #
    def _filter_list(self, list_widget: QListWidget, text: str):
        text = text.strip()
        for row in range(list_widget.count()):
            item = list_widget.item(row)
            item.setHidden(bool(text) and text not in item.text())

    def _checked_ids(self, list_widget: QListWidget):
        return [
            list_widget.item(row).data(Qt.UserRole)
            for row in range(list_widget.count())
            if list_widget.item(row).checkState() == Qt.Checked
        ]