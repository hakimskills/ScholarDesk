# -*- coding: utf-8 -*-
"""
app/ui/students.py

The Students list page. Shows the full student roster with search,
class/payment filters and per-row actions. Pure UI with sample data —
replace `_sample_students()` with a real query against app/services
once the SQLite layer is ready.
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QFrame,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from app.theme import Colors
from app.common import ScrollPage, make_label, make_button

# status_key -> (display text, text color, background color)
_PAYMENT_STATUS = {
    "paid": ("مسدد", Colors.SUCCESS, Colors.SUCCESS_LIGHT),
    "partial": ("جزئي", Colors.WARNING, Colors.WARNING_LIGHT),
    "unpaid": ("غير مسدد", Colors.DANGER, Colors.DANGER_LIGHT),
}
_COLUMNS = ["الاسم", "القسم", "ولي الأمر", "الهاتف", "تاريخ التسجيل", "حالة الدفع", "إجراءات"]

_SAMPLE_STUDENTS = [
    {"name": "ياسين بلحاج", "class_name": "السنة 3", "guardian": "محمد بلحاج", "phone": "0551 23 45 67", "joined_at": "12/09/2025", "payment_status": "paid"},
    {"name": "مريم عبد الرحمان", "class_name": "تحضيري", "guardian": "سمير عبد الرحمان", "phone": "0662 34 56 78", "joined_at": "03/10/2025", "payment_status": "paid"},
    {"name": "عمر شريف", "class_name": "السنة 2", "guardian": "كريم شريف", "phone": "0770 45 67 89", "joined_at": "20/09/2025", "payment_status": "unpaid"},
    {"name": "لينا مرابط", "class_name": "السنة 5", "guardian": "فريد مرابط", "phone": "0554 56 78 90", "joined_at": "05/09/2025", "payment_status": "partial"},
    {"name": "آدم بوزيد", "class_name": "السنة 1", "guardian": "ياسمين بوزيد", "phone": "0661 67 89 01", "joined_at": "18/09/2025", "payment_status": "paid"},
    {"name": "نور الهدى قاسمي", "class_name": "السنة 4", "guardian": "عبد القادر قاسمي", "phone": "0772 78 90 12", "joined_at": "02/10/2025", "payment_status": "unpaid"},
    {"name": "إلياس حمدي", "class_name": "السنة 3", "guardian": "رشيد حمدي", "phone": "0553 89 01 23", "joined_at": "14/09/2025", "payment_status": "paid"},
    {"name": "سارة بن عيسى", "class_name": "تحضيري", "guardian": "نبيل بن عيسى", "phone": "0663 90 12 34", "joined_at": "27/09/2025", "payment_status": "partial"},
]


class StudentsPage(ScrollPage):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        self._students = _SAMPLE_STUDENTS
        super().__init__(spacing=18, parent=parent)

        self.content_layout.addLayout(self._build_header())
        self.content_layout.addLayout(self._build_toolbar())
        self.content_layout.addWidget(self._build_table_card())

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
        title_box.addWidget(make_label(f"{len(self._students)} طالب مسجل في المدرسة", "pageSubtitle"))
        header.addLayout(title_box)
        header.addStretch(1)

        header.addWidget(make_button("⬇  تصدير", "outlineButton"))
        header.addWidget(make_button("+  إضافة طالب", "primaryButton"))
        return header

    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText("🔍  ابحث بالاسم، الهاتف أو ولي الأمر...")
        search_box.setAlignment(Qt.AlignRight)
        toolbar.addWidget(search_box, 1)

        class_filter = QComboBox(objectName="filterCombo")
        class_filter.addItems(["كل الأقسام", "تحضيري", "السنة 1", "السنة 2", "السنة 3", "السنة 4", "السنة 5"])
        toolbar.addWidget(class_filter)

        status_filter = QComboBox(objectName="filterCombo")
        status_filter.addItems(["كل حالات الدفع", "مسدد", "جزئي", "غير مسدد"])
        toolbar.addWidget(status_filter)

        return toolbar

    def _build_table_card(self) -> QFrame:
        card = QFrame(objectName="tableCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        table = QTableWidget()
        table.setObjectName("dataTable")
        table.setLayoutDirection(Qt.RightToLeft)
        table.setColumnCount(len(_COLUMNS))
        table.setHorizontalHeaderLabels(_COLUMNS)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(58)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, len(_COLUMNS) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(len(_COLUMNS) - 1, QHeaderView.Fixed)
        table.setColumnWidth(len(_COLUMNS) - 1, 100)

        table.setRowCount(len(self._students))
        for row, student in enumerate(self._students):
            table.setCellWidget(row, 0, self._build_name_cell(student["name"]))
            for col, key in enumerate(("class_name", "guardian", "phone", "joined_at"), start=1):
                table.setItem(row, col, self._build_text_item(student[key]))
            table.setCellWidget(row, 5, self._build_status_cell(student["payment_status"]))
            table.setCellWidget(row, 6, self._build_actions_cell())

        layout.addWidget(table)
        return card

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

    def _build_actions_cell(self) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        row.addStretch(1)
        for icon in ("👁", "✏", "🗑"):
            row.addWidget(make_button(icon, "rowActionButton"))
        row.addStretch(1)
        return wrapper