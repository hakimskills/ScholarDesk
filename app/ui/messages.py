# -*- coding: utf-8 -*-
"""
app/ui/messages.py

The Messages (الرسائل) page. Send an SMS to:
- جميع التلاميذ  — every student in the database.
- فوج معيّن       — every student enrolled in one chosen group (فوج).
- تحديد يدوي      — whichever students you check by hand.

Whatever the mode, the right-hand table always shows exactly who
will receive the message (full name + phone number), and lets you
fine-tune the selection with the checkboxes before sending — e.g.
uncheck one student out of a group without leaving "فوج معيّن" mode.

Sending itself goes through app/services/message_service.py, which
is currently a stub (no real SMS gateway wired up yet) — see that
file for where to plug one in.

Mirrors the page shell/table/dialog conventions used by
app/ui/students.py, app/ui/groups.py and app/ui/teachers.py, and
reuses SectionCard from app/widgets for both halves of the page so
it reads as part of the same app rather than a bolted-on screen.
"""

from typing import List

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QFrame,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QWidget, QMessageBox, QTextEdit, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from app.theme import Colors
from app.common import ScrollPage, make_label, make_button
from app.widgets import SectionCard
from app.services import student_service, group_service, message_service

_COLUMNS = ["الاسم الكامل", "الهاتف"]
_NAME_COLUMN, _PHONE_COLUMN = 0, 1

_MODE_ALL = "جميع التلاميذ"
_MODE_GROUP = "فوج معيّن"
_MODE_MANUAL = "تحديد يدوي"
_MODES = [_MODE_ALL, _MODE_GROUP, _MODE_MANUAL]

_TEXTEDIT_STYLE = f"""
QTextEdit {{
    background-color: {Colors.SURFACE_ALT};
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 12.5px;
    color: {Colors.TEXT_PRIMARY};
}}
QTextEdit:focus {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.PRIMARY};
}}
"""


class MessagesPage(ScrollPage):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(spacing=18, parent=parent)
        self._all_groups = []  # populated on each reload, in case a group was added elsewhere

        self.content_layout.addLayout(self._build_header())
        self.content_layout.addLayout(self._build_main_row())

        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        self.search_box.textChanged.connect(self._on_search_changed)
        self.message_input.textChanged.connect(self._update_char_count)

        self._reload_groups()
        self._on_mode_changed()

    # ------------------------------------------------------------------ #
    # Header
    # ------------------------------------------------------------------ #
    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(6)
        title_box.addWidget(make_button(
            "→  رجوع للوحة التحكم", "linkButton",
            on_click=lambda: self.navigate_requested.emit("dashboard"),
        ))
        title_box.addWidget(make_label("الرسائل", "pageTitle"))

        self.recipients_label = make_label("", "statPill")
        self.recipients_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title_box.addWidget(self.recipients_label)

        header.addLayout(title_box)
        header.addStretch(1)
        return header

    # ------------------------------------------------------------------ #
    # Main row: compose panel (right, in RTL) + recipient table (left)
    # ------------------------------------------------------------------ #
    def _build_main_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)
        row.addWidget(self._build_compose_section(), 1)
        row.addWidget(self._build_recipients_section(), 1)
        return row

    def _build_compose_section(self) -> SectionCard:
        section = SectionCard(title="إعداد الرسالة", subtitle="اختر المستلمين واكتب نص الرسالة")

        self.mode_combo = QComboBox(objectName="formCombo")
        self.mode_combo.addItems(_MODES)
        section.add_widget(make_label("إرسال إلى", "formFieldLabel"))
        section.add_widget(self.mode_combo)

        self.group_combo = QComboBox(objectName="formCombo")
        self.group_label = make_label("الفوج", "formFieldLabel")
        section.add_widget(self.group_label)
        section.add_widget(self.group_combo)

        self.message_input = QTextEdit()
        self.message_input.setStyleSheet(_TEXTEDIT_STYLE)
        self.message_input.setPlaceholderText("اكتب نص الرسالة هنا...")
        self.message_input.setMinimumHeight(160)
        section.add_widget(make_label("نص الرسالة", "formFieldLabel"))
        section.add_widget(self.message_input)

        self.char_count_label = make_label(
            "0 حرف  •  الرسالة الواحدة تتسع لحوالي 160 حرفاً",
            style=f"color: {Colors.TEXT_MUTED}; font-size: 11px;",
        )
        section.add_widget(self.char_count_label)

        section.add_widget(make_button("📩  إرسال الرسالة", "primaryButton", on_click=self._on_send_clicked))

        return section

    def _build_recipients_section(self) -> SectionCard:
        section = SectionCard(title="اختيار المستلمين")

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setLayoutDirection(Qt.RightToLeft)
        self.search_box.setPlaceholderText("🔍  ابحث بالاسم أو الهاتف...")
        self.search_box.setAlignment(Qt.AlignRight)
        toolbar.addWidget(self.search_box, 1)

        toolbar.addWidget(make_button("تحديد الكل", "outlineButton", on_click=self._select_all))
        toolbar.addWidget(make_button("إلغاء التحديد", "outlineButton", on_click=self._deselect_all))
        section.add_layout(toolbar)

        section.add_widget(self._build_table_card())
        return section

    def _build_table_card(self) -> QFrame:
        card = QFrame(objectName="tableCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setLayoutDirection(Qt.RightToLeft)
        self.table.setColumnCount(len(_COLUMNS))
        self.table.setHorizontalHeaderLabels(_COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setMinimumHeight(360)
        self.table.verticalHeader().setDefaultSectionSize(46)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(_NAME_COLUMN, QHeaderView.Stretch)
        header.setSectionResizeMode(_PHONE_COLUMN, QHeaderView.ResizeToContents)

        self.table.itemChanged.connect(self._on_item_changed)

        layout.addWidget(self.table)
        return card

    # ------------------------------------------------------------------ #
    # Mode / group / search handling
    # ------------------------------------------------------------------ #
    def _reload_groups(self):
        self._all_groups = group_service.get_all_groups()
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        for group in self._all_groups:
            self.group_combo.addItem(group.display_name or "—", userData=group.id)
        self.group_combo.blockSignals(False)

    def _on_mode_changed(self, *_):
        mode = self.mode_combo.currentText()
        self.group_combo.setVisible(mode == _MODE_GROUP)
        self.group_label.setVisible(mode == _MODE_GROUP)
        self._reload_table()

    def _on_group_changed(self, *_):
        if self.mode_combo.currentText() == _MODE_GROUP:
            self._reload_table()

    def _on_search_changed(self, text: str):
        text = text.strip()
        for row in range(self.table.rowCount()):
            name = self.table.item(row, _NAME_COLUMN).text()
            phone = self.table.item(row, _PHONE_COLUMN).text()
            self.table.setRowHidden(row, bool(text) and text not in name and text not in phone)

    def _reload_table(self):
        """Repopulate the table for the current mode, with checkboxes
        pre-set the way each mode implies (all/group -> checked,
        manual -> unchecked) — the checkboxes stay editable
        afterwards either way, so any mode can still be fine-tuned."""
        mode = self.mode_combo.currentText()

        if mode == _MODE_GROUP:
            group_id = self.group_combo.currentData()
            students = group_service.get_students_for_group(group_id) if group_id is not None else []
            default_checked = True
        elif mode == _MODE_ALL:
            students = student_service.get_all_students()
            default_checked = True
        else:  # manual
            students = student_service.get_all_students()
            default_checked = False

        self.table.blockSignals(True)
        self.table.setRowCount(len(students))
        for row, student in enumerate(students):
            name_item = QTableWidgetItem(student.full_name or "—")
            name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
            name_item.setCheckState(Qt.Checked if default_checked else Qt.Unchecked)
            name_item.setData(Qt.UserRole, student.phone)
            self.table.setItem(row, _NAME_COLUMN, name_item)

            phone_item = QTableWidgetItem(student.phone or "—")
            phone_item.setFlags(phone_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, _PHONE_COLUMN, phone_item)
        self.table.blockSignals(False)

        self.search_box.clear()
        self._update_recipients_label()

    def _on_item_changed(self, item: QTableWidgetItem):
        if item.column() == _NAME_COLUMN:
            self._update_recipients_label()

    # ------------------------------------------------------------------ #
    # Selection helpers
    # ------------------------------------------------------------------ #
    def _select_all(self):
        self._set_all_checked(Qt.Checked)

    def _deselect_all(self):
        self._set_all_checked(Qt.Unchecked)

    def _set_all_checked(self, state):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                self.table.item(row, _NAME_COLUMN).setCheckState(state)
        self.table.blockSignals(False)
        self._update_recipients_label()

    def _checked_phone_numbers(self) -> List[str]:
        numbers = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, _NAME_COLUMN)
            if item.checkState() == Qt.Checked:
                phone = item.data(Qt.UserRole)
                if phone:
                    numbers.append(phone)
        return numbers

    def _update_recipients_label(self):
        count = sum(
            1 for row in range(self.table.rowCount())
            if self.table.item(row, _NAME_COLUMN).checkState() == Qt.Checked
        )
        self.recipients_label.setText(f"📨  {count} مستلم محدد")

    def _update_char_count(self):
        length = len(self.message_input.toPlainText())
        self.char_count_label.setText(f"{length} حرف  •  الرسالة الواحدة تتسع لحوالي 160 حرفاً")

    # ------------------------------------------------------------------ #
    # Send
    # ------------------------------------------------------------------ #
    def _on_send_clicked(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "الرسالة فارغة", "الرجاء كتابة نص الرسالة قبل الإرسال.")
            return

        phone_numbers = self._checked_phone_numbers()
        if not phone_numbers:
            QMessageBox.warning(self, "لا يوجد مستلمون", "الرجاء تحديد تلميذ واحد على الأقل لإرسال الرسالة إليه.")
            return

        if not self._confirm_send(len(phone_numbers)):
            return

        success, failed = message_service.send_sms(phone_numbers, message)

        box = QMessageBox(self)
        box.setWindowTitle("نتيجة الإرسال")
        box.setLayoutDirection(Qt.RightToLeft)
        if failed:
            box.setIcon(QMessageBox.Warning)
            box.setText(f"تم إرسال الرسالة إلى {len(success)} مستلم، وفشل الإرسال إلى {len(failed)}.")
        else:
            box.setIcon(QMessageBox.Information)
            box.setText(f"تم إرسال الرسالة بنجاح إلى {len(success)} مستلم.")
        box.addButton("موافق", QMessageBox.AcceptRole)
        box.exec()

    def _confirm_send(self, count: int) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle("تأكيد الإرسال")
        box.setText(f"هل تريد إرسال هذه الرسالة إلى {count} مستلم؟")
        box.setIcon(QMessageBox.Question)
        box.setLayoutDirection(Qt.RightToLeft)

        yes_button = box.addButton("إرسال", QMessageBox.YesRole)
        no_button = box.addButton("إلغاء", QMessageBox.NoRole)
        box.setDefaultButton(no_button)

        box.exec()
        return box.clickedButton() == yes_button