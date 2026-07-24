# -*- coding: utf-8 -*-
"""
app/ui/students.py

The Students list page. Shows the student roster with live search,
class/payment filters and per-row actions, backed by
app/services/student_service.py (SQLite).
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
from app.services import student_service

# status_key -> (display text, text color, background color)
_PAYMENT_STATUS = {
    "paid": ("مسدد", Colors.SUCCESS, Colors.SUCCESS_LIGHT),
    "partial": ("جزئي", Colors.WARNING, Colors.WARNING_LIGHT),
    "unpaid": ("غير مسدد", Colors.DANGER, Colors.DANGER_LIGHT),
}
_STATUS_LABEL_TO_KEY = {label: key for key, (label, _, _) in _PAYMENT_STATUS.items()}
_COLUMNS = ["الاسم", "القسم", "ولي الأمر", "الهاتف", "تاريخ التسجيل", "حالة الدفع", "إجراءات"]
_CLASS_OPTIONS = ["كل الأقسام", "تحضيري", "السنة 1", "السنة 2", "السنة 3", "السنة 4", "السنة 5"]
_STATUS_OPTIONS = ["كل حالات الدفع"] + [label for label, _, _ in _PAYMENT_STATUS.values()]


class StudentsPage(ScrollPage):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(spacing=18, parent=parent)

        self.content_layout.addLayout(self._build_header())
        self.content_layout.addLayout(self._build_toolbar())
        self.content_layout.addWidget(self._build_table_card())

        self.search_box.textChanged.connect(self._reload)
        self.class_filter.currentIndexChanged.connect(self._reload)
        self.status_filter.currentIndexChanged.connect(self._reload)

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
        title_box.addWidget(make_label("الطلاب", "pageTitle"))
        self.subtitle_label = make_label("", "pageSubtitle")
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box)
        header.addStretch(1)

        header.addWidget(make_button("⬇  تصدير", "outlineButton"))
        header.addWidget(make_button("+  إضافة طالب", "primaryButton"))
        return header

    # ------------------------------------------------------------------ #
    # Search + filters
    # ------------------------------------------------------------------ #
    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍  ابحث بالاسم، الهاتف أو ولي الأمر...")
        self.search_box.setAlignment(Qt.AlignRight)
        toolbar.addWidget(self.search_box, 1)

        self.class_filter = QComboBox(objectName="filterCombo")
        self.class_filter.addItems(_CLASS_OPTIONS)
        toolbar.addWidget(self.class_filter)

        self.status_filter = QComboBox(objectName="filterCombo")
        self.status_filter.addItems(_STATUS_OPTIONS)
        toolbar.addWidget(self.status_filter)

        return toolbar

    def _current_filters(self):
        class_name = self.class_filter.currentText()
        if class_name == _CLASS_OPTIONS[0]:
            class_name = ""

        status_label = self.status_filter.currentText()
        status_key = _STATUS_LABEL_TO_KEY.get(status_label, "")

        return self.search_box.text().strip(), class_name, status_key

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
        search, class_name, status_key = self._current_filters()
        students = student_service.get_all_students(
            search=search, class_name=class_name, payment_status=status_key,
        )

        total = student_service.count_students()
        self.subtitle_label.setText(f"{total} طالب مسجل في المدرسة")

        self.table.setRowCount(len(students))
        for row, student in enumerate(students):
            self.table.setCellWidget(row, 0, self._build_name_cell(student.name))
            for col, value in enumerate(
                (student.class_name, student.guardian, student.phone, student.joined_at), start=1
            ):
                self.table.setItem(row, col, self._build_text_item(value))
            self.table.setCellWidget(row, 5, self._build_status_cell(student.payment_status))
            self.table.setCellWidget(row, 6, self._build_actions_cell(student.id))

    def _build_name_cell(self, name: str) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(12, 4, 12, 4)
        row.addWidget(make_label(name, style=f"font-size: 12.5px; font-weight: 600; color: {Colors.TEXT_PRIMARY};"))
        row.addStretch(1)
        return wrapper

    def _build_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setForeground(QBrush(QColor(Colors.TEXT_SECONDARY)))
        return item

    def _build_status_cell(self, status_key: str) -> QWidget:
        text, color, bg = _PAYMENT_STATUS.get(status_key, ("—", Colors.TEXT_MUTED, Colors.SURFACE_ALT))
        badge = make_label(
            text, "statusBadge",
            style=f"background-color: {bg}; color: {color}; border-radius: 10px; padding: 3px 10px; font-size: 11.5px; font-weight: 600;",
        )

        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch(1)
        row.addWidget(badge)
        row.addStretch(1)
        return wrapper

    def _build_actions_cell(self, student_id: int) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        row.addStretch(1)
        row.addWidget(make_button("👁", "rowActionButton"))
        row.addWidget(make_button("✏", "rowActionButton"))
        row.addWidget(make_button(
            "🗑", "rowActionButton",
            on_click=lambda: self._confirm_delete(student_id),
        ))
        row.addStretch(1)
        return wrapper

    def _confirm_delete(self, student_id: int):
        answer = QMessageBox.question(
            self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا الطالب؟",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            student_service.delete_student(student_id)
            self._reload()