# -*- coding: utf-8 -*-
"""
app/ui/message_compose_dialog.py

"كتابة الرسالة" — the message text is deliberately not shown on
app/ui/messages.py itself. Once recipients are picked there and
"متابعة لكتابة الرسالة" is clicked, THIS dialog opens with the
recipient list already locked in, and is the only place the message
body is written and sent from.

Styled with the same formDialog/formCard building blocks used by
app/ui/group_students_dialog.py and app/ui/group_form.py so it reads
as part of the same app.
"""

from typing import List

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QMessageBox
from PySide6.QtCore import Qt

from app.theme import Colors
from app.common import make_label, make_button
from app.models.student import Student
from app.services import message_service

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


class MessageComposeDialog(QDialog):
    """Compose and send one SMS to an already-chosen list of students."""

    def __init__(self, recipients: List[Student], parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._recipients = recipients
        self.setWindowTitle("كتابة الرسالة")
        self.setMinimumWidth(460)

        self._build_ui()
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
        header.addWidget(make_label("كتابة الرسالة", "formTitle", align=Qt.AlignRight))
        header.addWidget(make_label(
            f"سيتم الإرسال إلى {len(self._recipients)} مستلم", "formSubtitle", align=Qt.AlignRight,
        ))
        outer.addLayout(header)

        card = QFrame(objectName="formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        card_layout.addWidget(make_label("المستلمون", "formFieldLabel"))
        names_preview = "، ".join(student.full_name or "—" for student in self._recipients)
        preview_label = make_label(
            names_preview, style=f"color: {Colors.TEXT_SECONDARY}; font-size: 11.5px;",
        )
        preview_label.setWordWrap(True)
        card_layout.addWidget(preview_label)

        card_layout.addWidget(make_label("نص الرسالة", "formFieldLabel"))
        self.message_input = QTextEdit()
        self.message_input.setStyleSheet(_TEXTEDIT_STYLE)
        self.message_input.setPlaceholderText("اكتب نص الرسالة هنا...")
        self.message_input.setMinimumHeight(170)
        self.message_input.textChanged.connect(self._update_char_count)
        card_layout.addWidget(self.message_input)

        self.char_count_label = make_label(
            "0 حرف  •  الرسالة الواحدة تتسع لحوالي 160 حرفاً",
            style=f"color: {Colors.TEXT_MUTED}; font-size: 11px;",
        )
        card_layout.addWidget(self.char_count_label)

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
        row.addWidget(make_button("رجوع", "outlineButton", on_click=self.reject))
        row.addStretch(1)
        row.addWidget(make_button("📩  إرسال", "primaryButton", on_click=self._on_send_clicked))
        return row

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

        if not self._confirm_send():
            return

        phone_numbers = [student.phone for student in self._recipients if student.phone]
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

        self.accept()

    def _confirm_send(self) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle("تأكيد الإرسال")
        box.setText(f"هل تريد إرسال هذه الرسالة إلى {len(self._recipients)} مستلم؟")
        box.setIcon(QMessageBox.Question)
        box.setLayoutDirection(Qt.RightToLeft)

        yes_button = box.addButton("إرسال", QMessageBox.YesRole)
        no_button = box.addButton("إلغاء", QMessageBox.NoRole)
        box.setDefaultButton(no_button)

        box.exec()
        return box.clickedButton() == yes_button