# -*- coding: utf-8 -*-
"""
app/ui/students.py

The Students list page. Shows the student roster with live search,
class/payment filters and per-row actions, backed by
app/services/student_service.py (SQLite).

New students are added without a class (class assignment happens
later, via the edit dialog) — so this page also has to render and
filter on an empty class_name gracefully.
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
from app.constants import PAYMENT_STATUS, STATUS_LABEL_TO_KEY, CLASS_OPTIONS, UNASSIGNED_CLASS_LABEL
from app.models.student import UNASSIGNED_CLASS
from app.services import student_service
from app.ui.student_form import StudentFormDialog

_COLUMNS = ["الاسم", "القسم", "ولي الأمر", "الهاتف", "تاريخ التسجيل", "حالة الدفع", "إجراءات"]

# "كل الأقسام" (all) + real classes + "غير محدد" (students not yet
# assigned to a class) at the end, so it's filterable too.
_ALL_CLASSES_LABEL = "كل الأقسام"
_CLASS_OPTIONS = [_ALL_CLASSES_LABEL] + CLASS_OPTIONS + [UNASSIGNED_CLASS_LABEL]
_STATUS_OPTIONS = ["كل حالات الدفع"] + [label for label, _, _ in PAYMENT_STATUS.values()]


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
        header.addWidget(make_button("+  إضافة طالب", "primaryButton", on_click=self._open_add_form))
        return header

    def _open_add_form(self):
        # No class field here on purpose — new students are registered
        # first and assigned to a class later via the edit dialog.
        dialog = StudentFormDialog(parent=self)
        if dialog.exec() == StudentFormDialog.Accepted:
            self._reload()

    def _open_edit_form(self, student_id: int):
        student = student_service.get_student(student_id)
        if student is None:
            return
        dialog = StudentFormDialog(student=student, parent=self)
        if dialog.exec() == StudentFormDialog.Accepted:
            self._reload()

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
        if class_name == _ALL_CLASSES_LABEL:
            class_name = ""
        elif class_name == UNASSIGNED_CLASS_LABEL:
            class_name = UNASSIGNED_CLASS  # i.e. "" — filtered explicitly below
        # NOTE: both "all" and "unassigned" resolve to an empty string
        # for UNASSIGNED_CLASS, so we track "is a filter active" apart
        # from the value itself.
        filter_by_unassigned = self.class_filter.currentText() == UNASSIGNED_CLASS_LABEL

        status_label = self.status_filter.currentText()
        status_key = STATUS_LABEL_TO_KEY.get(status_label, "")

        return self.search_box.text().strip(), class_name, status_key, filter_by_unassigned

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
        search, class_name, status_key, filter_by_unassigned = self._current_filters()
        students = student_service.get_all_students(
            search=search, class_name=class_name, payment_status=status_key,
        )
        if filter_by_unassigned:
            students = [s for s in students if not s.has_class]

        total = student_service.count_students()
        self.subtitle_label.setText(f"{total} طالب مسجل في المدرسة")

        self.table.setRowCount(len(students))
        for row, student in enumerate(students):
            self.table.setCellWidget(row, 0, self._build_name_cell(student.full_name))
            self.table.setCellWidget(row, 1, self._build_class_cell(student.class_name))
            for col, value in enumerate((student.guardian, student.phone, student.joined_at), start=2):
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

    def _build_class_cell(self, class_name: str) -> QWidget:
        """Shows the class name, or a muted 'غير محدد' badge if not assigned yet."""
        if class_name:
            label = make_label(class_name, style=f"font-size: 12.5px; color: {Colors.TEXT_SECONDARY};")
        else:
            label = make_label(
                UNASSIGNED_CLASS_LABEL,
                style=(
                    f"font-size: 11.5px; font-weight: 600; color: {Colors.TEXT_MUTED};"
                    f"background-color: {Colors.SURFACE_ALT}; border-radius: 10px; padding: 3px 10px;"
                ),
            )
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(label)
        row.addStretch(1)
        return wrapper

    def _build_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setForeground(QBrush(QColor(Colors.TEXT_SECONDARY)))
        return item

    def _build_status_cell(self, status_key: str) -> QWidget:
        text, color, bg = PAYMENT_STATUS.get(status_key, ("—", Colors.TEXT_MUTED, Colors.SURFACE_ALT))
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
        row.addWidget(make_button(
            "✏", "rowActionButton",
            on_click=lambda: self._open_edit_form(student_id),
        ))
        row.addWidget(make_button(
            "🗑", "rowActionButton",
            on_click=lambda: self._confirm_delete(student_id),
        ))
        row.addStretch(1)
        return wrapper

    def _confirm_delete(self, student_id: int):
        box = QMessageBox(self)
        box.setWindowTitle("تأكيد الحذف")
        box.setText("هل أنت متأكد من حذف هذا التلميذ؟")
        box.setIcon(QMessageBox.Question)
        box.setLayoutDirection(Qt.RightToLeft)
       
        yes_button = box.addButton("نعم", QMessageBox.YesRole)
        no_button = box.addButton("لا", QMessageBox.NoRole)
        box.setDefaultButton(no_button)
       
        box.exec()
        if box.clickedButton() == yes_button:
            student_service.delete_student(student_id)
            self._reload()