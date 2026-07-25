# -*- coding: utf-8 -*-
"""
app/ui/teacher_form.py

Add / edit teacher dialog — same fields shown in add and edit mode
(unlike students, a teacher has nothing that gets "assigned later").
Fields mirror the reference form: اللقب, الإسم, الجنس, المادة,
الإزدياد, العنوان, تسجيل, الهاتف. حساب جاري/بنكي and الملاحظة from
the reference form are intentionally left out.

Styled via the same formDialog/formCard/formInput rules in
app/theme.py used by student_form.py, including the scrollable body
so the buttons stay reachable on a short screen.

Saving talks to app/services/teacher_service.py directly — the
caller just needs to refresh its table after the dialog closes with
Accepted.
"""

from PySide6.QtWidgets import (
    QDialog, QGridLayout, QLineEdit, QComboBox, QDateEdit,
    QMessageBox, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel,
    QScrollArea,
)
from PySide6.QtCore import Qt, QDate

from app.constants import GENDER_OPTIONS, SUBJECT_OPTIONS
from app.models.teacher import Teacher
from app.services import teacher_service
from app.common import make_label, make_button

_DATE_FORMAT = "dd/MM/yyyy"
_UNSET = ""  # dropdown placeholder value, shown as "-"


def _make_date_edit() -> QDateEdit:
    date_edit = QDateEdit(objectName="formDate")
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat(_DATE_FORMAT)
    date_edit.setDate(QDate.currentDate())
    return date_edit


def _make_line_edit(placeholder: str = "") -> QLineEdit:
    line_edit = QLineEdit(objectName="formInput")
    line_edit.setAlignment(Qt.AlignRight)
    if placeholder:
        line_edit.setPlaceholderText(placeholder)
    return line_edit


def _make_combo(options) -> QComboBox:
    combo = QComboBox(objectName="formCombo")
    combo.addItem("-", userData=_UNSET)
    for option in options:
        combo.addItem(option, userData=option)
    return combo


def _field_box(label_text: str, widget: QWidget) -> QVBoxLayout:
    """Label stacked above its input — one cell of the two-column grid."""
    box = QVBoxLayout()
    box.setSpacing(6)
    box.addWidget(make_label(label_text, "formFieldLabel", align=Qt.AlignRight))
    box.addWidget(widget)
    return box


class TeacherFormDialog(QDialog):
    def __init__(self, teacher: Teacher = None, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._teacher = teacher
        self._is_edit = teacher is not None
        self.setWindowTitle("تعديل بيانات الأستاذ" if self._is_edit else "إضافة أستاذ جديد")
        self.setMinimumWidth(560)

        self._build_ui()
        if teacher:
            self._fill_from(teacher)
        self._fit_to_screen()

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 16)
        outer.setSpacing(14)

        outer.addLayout(self._build_header())

        card = QFrame(objectName="formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(20)

        card_layout.addLayout(self._build_personal_section())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_contact_section())

        scroll = QScrollArea()
        scroll.setObjectName("formScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setLayoutDirection(Qt.RightToLeft)
        scroll.setWidget(card)
        outer.addWidget(scroll, 1)

        outer.addLayout(self._build_buttons_row())

    def _fit_to_screen(self):
        """Cap the dialog's height to the available screen so the
        button row is never pushed off-screen; the card scrolls
        internally to make up the difference."""
        screen = self.screen() or (self.parent().screen() if self.parent() else None)
        if screen is None:
            return
        available = screen.availableGeometry()
        max_height = max(420, int(available.height() * 0.9))
        self.resize(self.width(), min(self.sizeHint().height(), max_height))
        self.setMaximumHeight(max_height)

    def _build_header(self) -> QVBoxLayout:
        header = QVBoxLayout()
        header.setSpacing(2)
        title = "تعديل بيانات الأستاذ" if self._is_edit else "إضافة أستاذ جديد"
        subtitle = "عدّل بيانات الأستاذ." if self._is_edit else "أدخل بيانات تسجيل الأستاذ."
        header.addWidget(make_label(title, "formTitle", align=Qt.AlignRight))
        header.addWidget(make_label(subtitle, "formSubtitle", align=Qt.AlignRight))
        return header

    def _separator(self) -> QFrame:
        line = QFrame(objectName="formHeaderSeparator")
        line.setFrameShape(QFrame.HLine)
        return line

    def _section_title(self, text: str) -> QLabel:
        return make_label(text, "formSectionTitle", align=Qt.AlignRight)

    # --- المعلومات الشخصية ---
    def _build_personal_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("المعلومات الشخصية"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        self.last_name_input = _make_line_edit()
        self.first_name_input = _make_line_edit()
        self.gender_input = _make_combo(GENDER_OPTIONS)
        self.birth_date_input = _make_date_edit()

        grid.addLayout(_field_box("اللقب *", self.last_name_input), 0, 0)
        grid.addLayout(_field_box("الإسم *", self.first_name_input), 0, 1)
        grid.addLayout(_field_box("الجنس", self.gender_input), 1, 0)
        grid.addLayout(_field_box("الإزدياد", self.birth_date_input), 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        section.addLayout(grid)
        return section

    # --- معلومات إضافية ---
    def _build_contact_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("معلومات إضافية"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        self.subject_input = _make_combo(SUBJECT_OPTIONS)
        self.address_input = _make_line_edit()
        self.phone_input = _make_line_edit("0551 23 45 67")
        self.joined_input = _make_date_edit()

        grid.addLayout(_field_box("المادة", self.subject_input), 0, 0)
        grid.addLayout(_field_box("العنوان", self.address_input), 0, 1)
        grid.addLayout(_field_box("الهاتف *", self.phone_input), 1, 0)
        grid.addLayout(_field_box("تاريخ التسجيل", self.joined_input), 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        section.addLayout(grid)
        return section

    def _build_buttons_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch(1)
        row.addWidget(make_button("إلغاء", "outlineButton", on_click=self.reject))
        row.addWidget(make_button("حفظ", "primaryButton", on_click=self._on_save))
        return row

    # ------------------------------------------------------------------ #
    # Fill / save
    # ------------------------------------------------------------------ #
    def _fill_from(self, teacher: Teacher):
        self.last_name_input.setText(teacher.last_name)
        self.first_name_input.setText(teacher.first_name)
        self.address_input.setText(teacher.address)
        self.phone_input.setText(teacher.phone)

        gender_idx = self.gender_input.findData(teacher.gender)
        self.gender_input.setCurrentIndex(max(gender_idx, 0))

        subject_idx = self.subject_input.findData(teacher.subject)
        self.subject_input.setCurrentIndex(max(subject_idx, 0))

        birth_date = QDate.fromString(teacher.birth_date, _DATE_FORMAT)
        if birth_date.isValid():
            self.birth_date_input.setDate(birth_date)

        joined = QDate.fromString(teacher.joined_at, _DATE_FORMAT)
        if joined.isValid():
            self.joined_input.setDate(joined)

    def _on_save(self):
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not last_name or not first_name or not phone:
            QMessageBox.warning(self, "بيانات ناقصة", "الرجاء تعبئة اللقب والإسم والهاتف.")
            return

        teacher = self._teacher or Teacher(first_name="", last_name="", phone="", joined_at="")
        teacher.last_name = last_name
        teacher.first_name = first_name
        teacher.gender = self.gender_input.currentData() or ""
        teacher.subject = self.subject_input.currentData() or ""
        teacher.birth_date = self.birth_date_input.date().toString(_DATE_FORMAT)
        teacher.address = self.address_input.text().strip()
        teacher.phone = phone
        teacher.joined_at = self.joined_input.date().toString(_DATE_FORMAT)

        if teacher.id is None:
            teacher_service.create_teacher(teacher)
        else:
            teacher_service.update_teacher(teacher)

        self.accept()