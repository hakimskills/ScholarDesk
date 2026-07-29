# -*- coding: utf-8 -*-
"""
app/ui/messages.py

The Messages (الرسائل) page. This page ONLY picks recipients — the
message text is never shown here on purpose. Once you've picked at
least one recipient and click "متابعة لكتابة الرسالة", the message
body and the actual send happen in a separate dialog
(app/ui/message_compose_dialog.py) that opens with the recipient
list already locked in.

Recipient picking mirrors app/ui/group_students_dialog.py's add/
remove pattern:
- RIGHT panel: "اختيار المستلمين" — a pool of students matching the
  current mode/search. Click one to add them to the message.
- LEFT panel: "المستلمون المحددون" — everyone you've added, each
  with a "✕" to remove them — which sends them straight back to the
  right-hand pool.

Reuses the pickRow/pickRowLabel/pickRowRemove/studentPickList
styling already defined in app/theme.py for
group_students_dialog.py, so this reads as the same interaction
pattern rather than a new one-off widget.
"""

from typing import List

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QComboBox,
    QListWidget, QListWidgetItem, QAbstractItemView, QLabel,
    QPushButton, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from app.theme import Colors
from app.common import ScrollPage, make_label, make_button
from app.widgets import SectionCard
from app.models.student import Student
from app.services import student_service, group_service
from app.ui.message_compose_dialog import MessageComposeDialog

_MODE_ALL = "الكل"
_MODE_GROUP = "فوج معيّن"
_MODES = [_MODE_ALL, _MODE_GROUP]


class _AvailableRow(QFrame):
    """One row in the right-hand pool. Click anywhere on it to add
    that student — no separate confirm step, it just moves left."""

    clicked = Signal()

    def __init__(self, student_id: int, name: str, phone: str, parent=None):
        super().__init__(parent)
        self.setObjectName("pickRow")
        self.student_id = student_id
        self.setCursor(Qt.PointingHandCursor)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setToolTip("انقر للإضافة إلى المستلمين")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(1)

        name_label = QLabel(name)
        name_label.setObjectName("pickRowLabel")
        name_label.setAlignment(Qt.AlignRight)
        layout.addWidget(name_label)

        phone_label = QLabel(phone or "بدون هاتف")
        phone_label.setAlignment(Qt.AlignRight)
        phone_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 10.5px; background: transparent;")
        layout.addWidget(phone_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class _ChosenRow(QFrame):
    """One row in the left-hand "المستلمون المحددون" list. Reuses the
    pickRow "selected" visual permanently, since being in this list
    already means selected. "✕" removes it — a pure UI move."""

    removed = Signal()

    def __init__(self, student_id: int, name: str, phone: str, parent=None):
        super().__init__(parent)
        self.setObjectName("pickRow")
        self.setProperty("selected", "true")
        self.student_id = student_id
        self.setLayoutDirection(Qt.RightToLeft)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        name_label = QLabel(name)
        name_label.setObjectName("pickRowLabel")
        name_label.setAlignment(Qt.AlignRight)
        text_box.addWidget(name_label)

        phone_label = QLabel(phone or "بدون هاتف")
        phone_label.setAlignment(Qt.AlignRight)
        phone_label.setStyleSheet(f"color: {Colors.PRIMARY_SOFT}; font-size: 10.5px; background: transparent;")
        text_box.addWidget(phone_label)
        layout.addLayout(text_box, 1)

        remove_button = QPushButton("✕")
        remove_button.setObjectName("pickRowRemove")
        remove_button.setFixedSize(20, 20)
        remove_button.setCursor(Qt.PointingHandCursor)
        remove_button.clicked.connect(self.removed.emit)
        layout.addWidget(remove_button, 0, Qt.AlignLeft)


def _make_pick_list(min_height: int) -> QListWidget:
    list_widget = QListWidget(objectName="studentPickList")
    list_widget.setLayoutDirection(Qt.RightToLeft)
    list_widget.setSelectionMode(QAbstractItemView.NoSelection)
    list_widget.setFocusPolicy(Qt.NoFocus)
    list_widget.setMinimumHeight(min_height)
    return list_widget


class MessagesPage(ScrollPage):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(spacing=18, parent=parent)
        self._all_groups = []
        self._available_students: List[Student] = []
        self._chosen_students: List[Student] = []  # order = the order they were added in

        self.content_layout.addLayout(self._build_header())
        self.content_layout.addLayout(self._build_main_row())

        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        self.search_box.textChanged.connect(self._populate_available_list)

        self._reload_groups()
        self._on_mode_changed()
        self._refresh_chosen_list()

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
    # Main row — picker (right, in RTL) + chosen list (left, in RTL)
    # ------------------------------------------------------------------ #
    def _build_main_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)
        row.addWidget(self._build_picker_section(), 1)   # added first -> right side in RTL
        row.addWidget(self._build_chosen_section(), 1)   # added second -> left side in RTL
        return row

    # ------------------------------------------------------------------ #
    # Right panel: mode + pool of students to click-to-add
    # ------------------------------------------------------------------ #
    def _build_picker_section(self) -> SectionCard:
        section = SectionCard(title="اختيار المستلمين", subtitle="انقر على تلميذ لإضافته إلى القائمة")

        self.mode_combo = QComboBox(objectName="formCombo")
        self.mode_combo.addItems(_MODES)
        section.add_widget(make_label("إرسال إلى", "formFieldLabel"))
        section.add_widget(self.mode_combo)

        self.group_combo = QComboBox(objectName="formCombo")
        self.group_label = make_label("الفوج", "formFieldLabel")
        section.add_widget(self.group_label)
        section.add_widget(self.group_combo)

        self.search_box = QLineEdit(objectName="formInput")
        self.search_box.setLayoutDirection(Qt.RightToLeft)
        self.search_box.setAlignment(Qt.AlignRight)
        self.search_box.setPlaceholderText("🔍  ابحث عن تلميذ...")
        section.add_widget(self.search_box)

        self.available_list = _make_pick_list(340)
        section.add_widget(self.available_list)

        footer = QHBoxLayout()
        self.available_count_label = make_label(
            "", style=f"color: {Colors.TEXT_MUTED}; font-size: 11px;",
        )
        footer.addWidget(self.available_count_label, 1)
        footer.addWidget(make_button("إضافة كل الظاهرين", "outlineButton", on_click=self._add_all_visible))
        section.add_layout(footer)

        return section

    # ------------------------------------------------------------------ #
    # Left panel: chosen recipients only — no message content here
    # ------------------------------------------------------------------ #
    def _build_chosen_section(self) -> SectionCard:
        section = SectionCard(title="المستلمون المحددون", subtitle="راجع القائمة ثم تابع لكتابة الرسالة")

        self.chosen_list = _make_pick_list(340)
        section.add_widget(self.chosen_list)

        section.add_widget(make_button(
            "متابعة لكتابة الرسالة  ←", "primaryButton",
            on_click=self._open_compose_dialog,
        ))

        return section

    # ------------------------------------------------------------------ #
    # Mode / group / search
    # ------------------------------------------------------------------ #
    def _reload_groups(self):
        self._all_groups = group_service.get_all_groups()
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        for group in self._all_groups:
            self.group_combo.addItem(group.display_name or "—", userData=group.id)
        self.group_combo.blockSignals(False)

    def _on_mode_changed(self, *_):
        is_group_mode = self.mode_combo.currentText() == _MODE_GROUP
        self.group_combo.setVisible(is_group_mode)
        self.group_label.setVisible(is_group_mode)
        self._reload_available()

    def _on_group_changed(self, *_):
        if self.mode_combo.currentText() == _MODE_GROUP:
            self._reload_available()

    def _current_pool(self) -> List[Student]:
        if self.mode_combo.currentText() == _MODE_GROUP:
            group_id = self.group_combo.currentData()
            return group_service.get_students_for_group(group_id) if group_id is not None else []
        return student_service.get_all_students()

    def _reload_available(self):
        chosen_ids = {s.id for s in self._chosen_students}
        self._available_students = [s for s in self._current_pool() if s.id not in chosen_ids]
        self.search_box.clear()
        self._populate_available_list()

    def _populate_available_list(self, *_):
        filter_text = self.search_box.text().strip()
        self.available_list.clear()

        shown = 0
        for student in self._available_students:
            name = student.full_name or "—"
            phone = student.phone or ""
            if filter_text and filter_text not in name and filter_text not in phone:
                continue

            item = QListWidgetItem()
            row = _AvailableRow(student.id, name, phone)
            row.clicked.connect(lambda sid=student.id: self._add_recipient(sid))
            item.setSizeHint(row.sizeHint())
            self.available_list.addItem(item)
            self.available_list.setItemWidget(item, row)
            shown += 1

        self.available_count_label.setText(
            f"{shown} تلميذ متاح للإضافة" if shown else "لا يوجد تلاميذ متاحون حالياً"
        )

    # ------------------------------------------------------------------ #
    # Add / remove recipients
    # ------------------------------------------------------------------ #
    def _add_recipient(self, student_id: int, refresh: bool = True):
        if any(s.id == student_id for s in self._chosen_students):
            return
        student = student_service.get_student(student_id)
        if student is None:
            return
        self._chosen_students.append(student)
        if refresh:
            self._reload_available()
            self._refresh_chosen_list()

    def _remove_recipient(self, student_id: int):
        self._chosen_students = [s for s in self._chosen_students if s.id != student_id]
        self._reload_available()
        self._refresh_chosen_list()

    def _add_all_visible(self):
        visible_ids = [
            self.available_list.itemWidget(self.available_list.item(i)).student_id
            for i in range(self.available_list.count())
        ]
        for student_id in visible_ids:
            self._add_recipient(student_id, refresh=False)
        self._reload_available()
        self._refresh_chosen_list()

    def _refresh_chosen_list(self):
        self.chosen_list.clear()
        for student in self._chosen_students:
            item = QListWidgetItem()
            row = _ChosenRow(student.id, student.full_name or "—", student.phone)
            row.removed.connect(lambda sid=student.id: self._remove_recipient(sid))
            item.setSizeHint(row.sizeHint())
            self.chosen_list.addItem(item)
            self.chosen_list.setItemWidget(item, row)

        self.recipients_label.setText(f"📨  {len(self._chosen_students)} مستلم محدد")

    # ------------------------------------------------------------------ #
    # Hand off to the compose dialog — recipients only get "confirmed"
    # by successfully clicking through to here.
    # ------------------------------------------------------------------ #
    def _open_compose_dialog(self):
        if not self._chosen_students:
            QMessageBox.warning(self, "لا يوجد مستلمون", "الرجاء إضافة تلميذ واحد على الأقل قبل المتابعة.")
            return

        dialog = MessageComposeDialog(recipients=list(self._chosen_students), parent=self)
        if dialog.exec() == MessageComposeDialog.Accepted:
            # Message was sent -> start fresh for the next one.
            self._chosen_students = []
            self._reload_available()
            self._refresh_chosen_list()