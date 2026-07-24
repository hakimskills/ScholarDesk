# -*- coding: utf-8 -*-
"""
app/ui/student_form.py

Add / edit student dialog, laid out as grouped two-column sections
(mirroring the reference school-software form): شخصية info, اتصال
info, then status. Styled via the formDialog/formCard/formInput
rules in app/theme.py.

- Add mode (student=None): collects registration info only — the
  fields mirrored from the reference form (اللقب, الإسم, الملف,
  الرمز, الإزدياد, المكان, الولي, العنوان, الهاتف, هاتف الولي,
  المؤسسة التعليمية) plus the app's own تسجيل/حالة الدفع fields.
  There is deliberately NO class field here — students are
  registered first and assigned to a class later.
- Edit mode (student=<existing>): same fields, PLUS the class combo,
  since assigning/changing the class happens through editing an
  existing student.

Either way, saving talks to app/services/student_service.py directly
— the caller just needs to refresh its table after the dialog closes
with Accepted.
"""

from PySide6.QtWidgets import (
    QDialog, QGridLayout, QLineEdit, QComboBox, QDateEdit,
    QMessageBox, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel,
    QScrollArea,
)
from PySide6.QtCore import Qt, QDate

from app.constants import CLASS_OPTIONS, PAYMENT_STATUS, UNASSIGNED_CLASS_LABEL
from app.models.student import Student, UNASSIGNED_CLASS
from app.services import student_service
from app.common import make_label, make_button

_DATE_FORMAT = "dd/MM/yyyy"


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


def _field_box(label_text: str, widget: QWidget) -> QVBoxLayout:
    """Label stacked above its input — one cell of the two-column grid."""
    box = QVBoxLayout()
    box.setSpacing(6)
    box.addWidget(make_label(label_text, "formFieldLabel", align=Qt.AlignRight))
    box.addWidget(widget)
    return box


class StudentFormDialog(QDialog):
    def __init__(self, student: Student = None, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._student = student
        self._is_edit = student is not None
        self.setWindowTitle("تعديل بيانات الطالب" if self._is_edit else "إضافة طالب جديد")
        self.setMinimumWidth(560)

        self._build_ui()
        if student:
            self._fill_from(student)
        self._fit_to_screen()

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 16)
        outer.setSpacing(14)

        # Header stays fixed at the top, outside the scroll area.
        outer.addLayout(self._build_header())

        card = QFrame(objectName="formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(20)

        card_layout.addLayout(self._build_personal_section())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_contact_section())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_status_section())

        # The card is the only part that scrolls — on a short screen
        # you can always reach the buttons below without resizing
        # the window, since they live outside this scroll area.
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
        title = "تعديل بيانات الطالب" if self._is_edit else "إضافة طالب جديد"
        subtitle = (
            "يمكنك هنا تعديل بيانات الطالب وإسناد القسم."
            if self._is_edit else
            "أدخل بيانات التسجيل الأساسية — يمكن إسناد القسم لاحقاً من نافذة التعديل."
        )
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
        self.file_number_input = _make_line_edit()
        self.code_input = _make_line_edit()
        self.birth_date_input = _make_date_edit()
        self.birth_place_input = _make_line_edit()

        grid.addLayout(_field_box("اللقب *", self.last_name_input), 0, 0)
        grid.addLayout(_field_box("الإسم *", self.first_name_input), 0, 1)
        grid.addLayout(_field_box("الملف", self.file_number_input), 1, 0)
        grid.addLayout(_field_box("الرمز", self.code_input), 1, 1)
        grid.addLayout(_field_box("الإزدياد", self.birth_date_input), 2, 0)
        grid.addLayout(_field_box("المكان", self.birth_place_input), 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        section.addLayout(grid)
        return section

    # --- معلومات الاتصال ---
    def _build_contact_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("معلومات الاتصال"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        self.guardian_input = _make_line_edit()
        self.guardian_phone_input = _make_line_edit()
        self.address_input = _make_line_edit()
        self.phone_input = _make_line_edit("0551 23 45 67")
        self.institution_input = _make_line_edit()
        self.joined_input = _make_date_edit()

        grid.addLayout(_field_box("الولي *", self.guardian_input), 0, 0)
        grid.addLayout(_field_box("هاتف الولي", self.guardian_phone_input), 0, 1)
        grid.addLayout(_field_box("العنوان", self.address_input), 1, 0)
        grid.addLayout(_field_box("الهاتف *", self.phone_input), 1, 1)
        grid.addLayout(_field_box("المؤسسة التعليمية", self.institution_input), 2, 0)
        grid.addLayout(_field_box("تاريخ التسجيل", self.joined_input), 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        section.addLayout(grid)
        return section

    # --- الحالة (القسم يُسند لاحقاً، لذا يظهر فقط عند التعديل) ---
    def _build_status_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("الحالة"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        self.status_input = QComboBox(objectName="formCombo")
        for key, (label, _, _) in PAYMENT_STATUS.items():
            self.status_input.addItem(label, userData=key)

        self.class_input = None
        if self._is_edit:
            self.class_input = QComboBox(objectName="formCombo")
            self.class_input.addItem(UNASSIGNED_CLASS_LABEL, userData=UNASSIGNED_CLASS)
            self.class_input.addItems(CLASS_OPTIONS)
            grid.addLayout(_field_box("القسم", self.class_input), 0, 0)
            grid.addLayout(_field_box("حالة الدفع", self.status_input), 0, 1)
        else:
            grid.addLayout(_field_box("حالة الدفع", self.status_input), 0, 0)
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
    def _fill_from(self, student: Student):
        self.last_name_input.setText(student.last_name)
        self.first_name_input.setText(student.first_name)
        self.file_number_input.setText(student.file_number)
        self.code_input.setText(student.code)
        self.birth_place_input.setText(student.birth_place)
        self.guardian_input.setText(student.guardian)
        self.guardian_phone_input.setText(student.guardian_phone)
        self.address_input.setText(student.address)
        self.phone_input.setText(student.phone)
        self.institution_input.setText(student.educational_institution)

        birth_date = QDate.fromString(student.birth_date, _DATE_FORMAT)
        if birth_date.isValid():
            self.birth_date_input.setDate(birth_date)

        joined = QDate.fromString(student.joined_at, _DATE_FORMAT)
        if joined.isValid():
            self.joined_input.setDate(joined)

        if self.class_input is not None:
            class_idx = self.class_input.findData(student.class_name)
            if class_idx < 0:
                class_idx = self.class_input.findText(student.class_name)
            self.class_input.setCurrentIndex(max(class_idx, 0))

        status_idx = self.status_input.findData(student.payment_status)
        if status_idx >= 0:
            self.status_input.setCurrentIndex(status_idx)

    def _on_save(self):
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        guardian = self.guardian_input.text().strip()
        phone = self.phone_input.text().strip()

        if not last_name or not first_name or not guardian or not phone:
            QMessageBox.warning(self, "بيانات ناقصة", "الرجاء تعبئة اللقب والإسم وولي الأمر والهاتف.")
            return

        student = self._student or Student(
            first_name="", last_name="", guardian="", phone="", joined_at="",
        )
        student.last_name = last_name
        student.first_name = first_name
        student.file_number = self.file_number_input.text().strip()
        student.code = self.code_input.text().strip()
        student.birth_date = self.birth_date_input.date().toString(_DATE_FORMAT)
        student.birth_place = self.birth_place_input.text().strip()
        student.joined_at = self.joined_input.date().toString(_DATE_FORMAT)
        student.guardian = guardian
        student.guardian_phone = self.guardian_phone_input.text().strip()
        student.address = self.address_input.text().strip()
        student.phone = phone
        student.educational_institution = self.institution_input.text().strip()
        student.payment_status = self.status_input.currentData()

        # Class is only ever touched in edit mode; new students stay
        # unassigned (class_name="") until assigned later.
        if self.class_input is not None:
            student.class_name = self.class_input.currentData()

        if student.id is None:
            student_service.create_student(student)
        else:
            student_service.update_student(student)

        self.accept()