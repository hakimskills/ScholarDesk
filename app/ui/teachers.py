# -*- coding: utf-8 -*-
"""
app/ui/teachers.py

The Teachers list page. Shows the teacher roster with live search
and subject/gender filters and per-row actions, backed by
app/services/teacher_service.py (SQLite). Mirrors app/ui/students.py.
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
from app.constants import SUBJECT_OPTIONS, GENDER_OPTIONS
from app.services import teacher_service
from app.ui.teacher_form import TeacherFormDialog

_COLUMNS = ["الاسم", "المادة", "الجنس", "الهاتف", "تاريخ التسجيل", "إجراءات"]

_ALL_SUBJECTS_LABEL = "كل المواد"
_ALL_GENDERS_LABEL = "الكل"
_SUBJECT_OPTIONS = [_ALL_SUBJECTS_LABEL] + SUBJECT_OPTIONS
_GENDER_OPTIONS = [_ALL_GENDERS_LABEL] + GENDER_OPTIONS


class TeachersPage(ScrollPage):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(spacing=18, parent=parent)

        self.content_layout.addLayout(self._build_header())
        self.content_layout.addLayout(self._build_toolbar())
        self.content_layout.addWidget(self._build_table_card())

        self.search_box.textChanged.connect(self._reload)
        self.subject_filter.currentIndexChanged.connect(self._reload)
        self.gender_filter.currentIndexChanged.connect(self._reload)

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
        title_box.addWidget(make_label("الأساتذة", "pageTitle"))
        self.subtitle_label = make_label("", "pageSubtitle")
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box)
        header.addStretch(1)

        header.addWidget(make_button("+  إضافة أستاذ", "primaryButton", on_click=self._open_add_form))
        return header

    def _open_add_form(self):
        dialog = TeacherFormDialog(parent=self)
        if dialog.exec() == TeacherFormDialog.Accepted:
            self._reload()

    def _open_edit_form(self, teacher_id: int):
        teacher = teacher_service.get_teacher(teacher_id)
        if teacher is None:
            return
        dialog = TeacherFormDialog(teacher=teacher, parent=self)
        if dialog.exec() == TeacherFormDialog.Accepted:
            self._reload()

    # ------------------------------------------------------------------ #
    # Search + filters
    # ------------------------------------------------------------------ #
    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍  ابحث بالاسم أو الهاتف...")
        self.search_box.setAlignment(Qt.AlignRight)
        toolbar.addWidget(self.search_box, 1)

        self.subject_filter = QComboBox(objectName="filterCombo")
        self.subject_filter.addItems(_SUBJECT_OPTIONS)
        toolbar.addWidget(self.subject_filter)

        self.gender_filter = QComboBox(objectName="filterCombo")
        self.gender_filter.addItems(_GENDER_OPTIONS)
        toolbar.addWidget(self.gender_filter)

        return toolbar

    def _current_filters(self):
        subject = self.subject_filter.currentText()
        if subject == _ALL_SUBJECTS_LABEL:
            subject = ""

        gender = self.gender_filter.currentText()
        if gender == _ALL_GENDERS_LABEL:
            gender = ""

        return self.search_box.text().strip(), subject, gender

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
        search, subject, gender = self._current_filters()
        teachers = teacher_service.get_all_teachers(search=search, subject=subject, gender=gender)

        total = teacher_service.count_teachers()
        self.subtitle_label.setText(f"{total} أستاذ مسجل في المدرسة")

        self.table.setRowCount(len(teachers))
        for row, teacher in enumerate(teachers):
            self.table.setCellWidget(row, 0, self._build_name_cell(teacher.full_name))
            for col, value in enumerate((teacher.subject, teacher.gender, teacher.phone, teacher.joined_at), start=1):
                self.table.setItem(row, col, self._build_text_item(value))
            self.table.setCellWidget(row, 5, self._build_actions_cell(teacher.id))

    def _build_name_cell(self, name: str) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(12, 4, 12, 4)
        row.addWidget(make_label(name, style=f"font-size: 12.5px; font-weight: 600; color: {Colors.TEXT_PRIMARY};"))
        row.addStretch(1)
        return wrapper

    def _build_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text or "—")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setForeground(QBrush(QColor(Colors.TEXT_SECONDARY)))
        return item

    def _build_actions_cell(self, teacher_id: int) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        row.addStretch(1)
        row.addWidget(make_button("👁", "rowActionButton"))
        row.addWidget(make_button(
            "✏", "rowActionButton",
            on_click=lambda: self._open_edit_form(teacher_id),
        ))
        row.addWidget(make_button(
            "🗑", "rowActionButton",
            on_click=lambda: self._confirm_delete(teacher_id),
        ))
        row.addStretch(1)
        return wrapper

    def _confirm_delete(self, teacher_id: int):
        box = QMessageBox(self)
        box.setWindowTitle("تأكيد الحذف")
        box.setText("هل أنت متأكد من حذف هذا الأستاذ؟")
        box.setIcon(QMessageBox.Question)
        box.setLayoutDirection(Qt.RightToLeft)
       
        yes_button = box.addButton("نعم", QMessageBox.YesRole)
        no_button = box.addButton("لا", QMessageBox.NoRole)
        box.setDefaultButton(no_button)
       
        box.exec()
        if box.clickedButton() == yes_button:
            teacher_service.delete_teacher(teacher_id)
            self._reload()