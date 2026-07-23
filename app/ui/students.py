# -*- coding: utf-8 -*-
"""
app/ui/students.py

The Students list page. Shows the full student roster with search,
class/payment filters and per-row actions. Pure UI with sample data —
replace `_sample_students()` with a real query against app/services
once the SQLite layer is ready.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QScrollArea, QFrame, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from app.theme import Colors


_PAYMENT_STATUS = {
    "paid": ("مسدد", "success"),
    "partial": ("جزئي", "warning"),
    "unpaid": ("غير مسدد", "danger"),
}


class StudentsPage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pageRoot")
        self.setLayoutDirection(Qt.RightToLeft)
        self._students = self._sample_students()
        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setLayoutDirection(Qt.RightToLeft)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        content.setObjectName("scrollContent")
        content.setLayoutDirection(Qt.RightToLeft)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 28)
        content_layout.setSpacing(18)

        content_layout.addLayout(self._build_header())
        content_layout.addLayout(self._build_toolbar())
        content_layout.addWidget(self._build_table_card())

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(16)

        back_btn = QPushButton("→  رجوع للوحة التحكم")
        back_btn.setObjectName("linkButton")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.navigate_requested.emit("dashboard"))

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.addWidget(back_btn)

        title = QLabel("الطلاب")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignRight)
        title_box.addWidget(title)

        subtitle = QLabel(f"{len(self._students)} طالب مسجل في المدرسة")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setAlignment(Qt.AlignRight)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch(1)

        export_btn = QPushButton("⬇  تصدير")
        export_btn.setObjectName("outlineButton")
        export_btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(export_btn)

        add_btn = QPushButton("+  إضافة طالب")
        add_btn.setObjectName("primaryButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(add_btn)

        return header

    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText("🔍  ابحث بالاسم، الهاتف أو ولي الأمر...")
        search_box.setAlignment(Qt.AlignRight)
        toolbar.addWidget(search_box, 1)

        class_filter = QComboBox()
        class_filter.setObjectName("filterCombo")
        class_filter.addItems(["كل الأقسام", "تحضيري", "السنة 1", "السنة 2", "السنة 3", "السنة 4", "السنة 5"])
        toolbar.addWidget(class_filter)

        status_filter = QComboBox()
        status_filter.setObjectName("filterCombo")
        status_filter.addItems(["كل حالات الدفع", "مسدد", "جزئي", "غير مسدد"])
        toolbar.addWidget(status_filter)

        return toolbar

    def _build_table_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("tableCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        columns = ["الاسم", "القسم", "ولي الأمر", "الهاتف", "تاريخ التسجيل", "حالة الدفع", "إجراءات"]

        table = QTableWidget()
        table.setObjectName("dataTable")
        table.setLayoutDirection(Qt.RightToLeft)
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setFocusPolicy(Qt.NoFocus)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setDefaultSectionSize(58)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, len(columns) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(len(columns) - 1, QHeaderView.Fixed)
        table.setColumnWidth(len(columns) - 1, 100)

        table.setRowCount(len(self._students))
        for row, student in enumerate(self._students):
            table.setCellWidget(row, 0, self._build_name_cell(student["name"]))
            table.setItem(row, 1, self._build_text_item(student["class_name"]))
            table.setItem(row, 2, self._build_text_item(student["guardian"]))
            table.setItem(row, 3, self._build_text_item(student["phone"]))
            table.setItem(row, 4, self._build_text_item(student["joined_at"]))
            table.setCellWidget(row, 5, self._build_status_cell(student["payment_status"]))
            table.setCellWidget(row, 6, self._build_actions_cell())

        layout.addWidget(table)
        return card

    def _build_name_cell(self, name: str) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(12, 4, 12, 4)
        row.setSpacing(10)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"font-size: 12.5px; font-weight: 600; color: {Colors.TEXT_PRIMARY};")
        row.addWidget(name_label)
        row.addStretch(1)
        return wrapper

    def _build_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setForeground(QBrush(QColor(Colors.TEXT_SECONDARY)))
        return item

    def _build_status_cell(self, status_key: str) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        text, kind = _PAYMENT_STATUS.get(status_key, ("—", "neutral"))
        row.addStretch(1)
        
        row.addStretch(1)
        return wrapper

    def _build_actions_cell(self) -> QWidget:
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        for icon in ("👁", "✏", "🗑"):
            btn = QPushButton(icon)
            btn.setObjectName("rowActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            row.addWidget(btn)
        row.insertStretch(0, 1)
        row.addStretch(1)
        return wrapper

    @staticmethod
    def _sample_students():
        return [
            {"name": "ياسين بلحاج", "class_name": "السنة 3", "guardian": "محمد بلحاج", "phone": "0551 23 45 67", "joined_at": "12/09/2025", "payment_status": "paid"},
            {"name": "مريم عبد الرحمان", "class_name": "تحضيري", "guardian": "سمير عبد الرحمان", "phone": "0662 34 56 78", "joined_at": "03/10/2025", "payment_status": "paid"},
            {"name": "عمر شريف", "class_name": "السنة 2", "guardian": "كريم شريف", "phone": "0770 45 67 89", "joined_at": "20/09/2025", "payment_status": "unpaid"},
            {"name": "لينا مرابط", "class_name": "السنة 5", "guardian": "فريد مرابط", "phone": "0554 56 78 90", "joined_at": "05/09/2025", "payment_status": "partial"},
            {"name": "آدم بوزيد", "class_name": "السنة 1", "guardian": "ياسمين بوزيد", "phone": "0661 67 89 01", "joined_at": "18/09/2025", "payment_status": "paid"},
            {"name": "نور الهدى قاسمي", "class_name": "السنة 4", "guardian": "عبد القادر قاسمي", "phone": "0772 78 90 12", "joined_at": "02/10/2025", "payment_status": "unpaid"},
            {"name": "إلياس حمدي", "class_name": "السنة 3", "guardian": "رشيد حمدي", "phone": "0553 89 01 23", "joined_at": "14/09/2025", "payment_status": "paid"},
            {"name": "سارة بن عيسى", "class_name": "تحضيري", "guardian": "نبيل بن عيسى", "phone": "0663 90 12 34", "joined_at": "27/09/2025", "payment_status": "partial"},
        ]