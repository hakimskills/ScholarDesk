# -*- coding: utf-8 -*-
"""
app/ui/groups.py

The Groups (فوج) list page. Shows every class/group with a live
search (matching level/subject/section) plus a section-letter
filter, the assigned teacher, and how many students are enrolled —
backed by app/services/group_service.py. Mirrors app/ui/students.py
and app/ui/teachers.py.

Unlike students/teachers, المستوى and المادة have no fixed list here
(schools name levels/subjects however they like), so there's no
dropdown filter for either — just the search box. الفوج (the section
letter) IS a small fixed set, so it gets its own filter dropdown.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QFrame,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QWidget, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from app.theme import Colors
from app.common import ScrollPage, make_label, make_button
from app.constants import SECTION_OPTIONS
from app.services import group_service, teacher_service
from app.ui.group_form import GroupFormDialog

_COLUMNS = ["الفصل", "المستوى", "المادة", "الفوج", "الأستاذ", "عدد التلاميذ", "إجراءات"]

_ALL_SECTIONS_LABEL = "كل الأفواج"
_SECTION_OPTIONS = [_ALL_SECTIONS_LABEL] + SECTION_OPTIONS
_NO_TEACHER_LABEL = "بدون أستاذ"


class GroupsPage(ScrollPage):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(spacing=18, parent=parent)

        self.content_layout.addLayout(self._build_header())
        self.content_layout.addLayout(self._build_toolbar())
        self.content_layout.addWidget(self._build_table_card())

        self.search_box.textChanged.connect(self._reload)
        self.section_filter.currentIndexChanged.connect(self._reload)

        self._reload()

    # ------------------------------------------------------------------ #
    # Header
    # ------------------------------------------------------------------ #
    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.addWidget(make_button(
            "→  رجوع للوحة التحكم", "linkButton",
            on_click=lambda: self.navigate_requested.emit("dashboard"),
        ))
        title_box.addWidget(make_label("الأفواج", "pageTitle"))
        self.subtitle_label = make_label("", "pageSubtitle")
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box)
        header.addStretch(1)

        header.addWidget(make_button("+  إضافة فوج", "primaryButton", on_click=self._open_add_form))
        return header

    def _open_add_form(self):
        dialog = GroupFormDialog(parent=self)
        if dialog.exec() == GroupFormDialog.Accepted:
            self._reload()

    def _open_edit_form(self, group_id: int):
        group = group_service.get_group(group_id)
        if group is None:
            return
        dialog = GroupFormDialog(group=group, parent=self)
        if dialog.exec() == GroupFormDialog.Accepted:
            self._reload()

    # ------------------------------------------------------------------ #
    # Search + filters
    # ------------------------------------------------------------------ #
    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍  ابحث بالمستوى أو المادة أو الفوج...")
        self.search_box.setAlignment(Qt.AlignRight)
        toolbar.addWidget(self.search_box, 1)

        self.section_filter = QComboBox(objectName="filterCombo")
        self.section_filter.addItems(_SECTION_OPTIONS)
        toolbar.addWidget(self.section_filter)

        return toolbar

    def _current_filters(self):
        section = self.section_filter.currentText()
        if section == _ALL_SECTIONS_LABEL:
            section = ""
        return self.search_box.text().strip(), section

    # ------------------------------------------------------------------ #
    # Table
    # ------------------------------------------------------------------ #
    def _build_table_card(self) -> QFrame:
        card = QFrame(objectName="tableCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setLayoutDirection(Qt.RightToLeft)
        self.table.setColumnCount(len(_COLUMNS))
        self.table.setHorizontalHeaderLabels(_COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(58)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, len(_COLUMNS) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(len(_COLUMNS) - 1, QHeaderView.Fixed)
        self.table.setColumnWidth(len(_COLUMNS) - 1, 100)

        layout.addWidget(self.table)
        return card

    def _reload(self):
        """Re-query the database with the current search/filter state and repaint the table."""
        search, section = self._current_filters()
        groups = group_service.get_all_groups(search=search, section=section)

        total = group_service.count_groups()
        self.subtitle_label.setText(f"{total} فوج مسجل")

        # One lookup for all teacher names instead of a query per row.
        teacher_names = {t.id: t.full_name for t in teacher_service.get_all_teachers()}

        self.table.setRowCount(len(groups))
        for row, group in enumerate(groups):
            teacher_label = teacher_names.get(group.teacher_id, _NO_TEACHER_LABEL)
            student_count = group_service.count_students_in_group(group.id)

            self.table.setCellWidget(row, 0, self._build_name_cell(group.display_name))
            for col, value in enumerate((group.level, group.subject, group.section, teacher_label), start=1):
                self.table.setItem(row, col, self._build_text_item(value))
            self.table.setItem(row, 5, self._build_text_item(str(student_count)))
            self.table.setCellWidget(row, 6, self._build_actions_cell(group.id))

    def _build_name_cell(self, name: str) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(12, 4, 12, 4)
        row.addWidget(make_label(
            name or "—", style=f"font-size: 12.5px; font-weight: 600; color: {Colors.TEXT_PRIMARY};",
        ))
        row.addStretch(1)
        return wrapper

    def _build_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text or "—")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setForeground(QBrush(QColor(Colors.TEXT_SECONDARY)))
        return item

    def _build_actions_cell(self, group_id: int) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        row.addStretch(1)
        row.addWidget(make_button("👁", "rowActionButton"))
        row.addWidget(make_button(
            "✏", "rowActionButton",
            on_click=lambda: self._open_edit_form(group_id),
        ))
        row.addWidget(make_button(
            "🗑", "rowActionButton",
            on_click=lambda: self._confirm_delete(group_id),
        ))
        row.addStretch(1)
        return wrapper

    def _confirm_delete(self, group_id: int):
        answer = QMessageBox.question(
            self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا الفوج؟",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            group_service.delete_group(group_id)
            self._reload()