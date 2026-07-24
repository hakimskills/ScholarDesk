# -*- coding: utf-8 -*-
"""
app/ui/student_form.py

Add / edit student dialog.

- Add mode (student=None): collects registration info only — the
  fields mirrored from the reference school-software form (اللقب,
  الإسم, الملف, الرمز, الإزدياد, المكان, الولي, العنوان, الهاتف,
  هاتف الولي, المؤسسة التعليمية) plus the app's own تسجيل/حالة الدفع
  fields. There is deliberately NO class field here — students are
  registered first and assigned to a class later.
- Edit mode (student=<existing>): same fields, PLUS the class combo,
  since assigning/changing the class happens through editing an
  existing student.

Either way, saving talks to app/services/student_service.py directly
— the caller just needs to refresh its table after the dialog closes
with Accepted.
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDialogButtonBox, QMessageBox, QVBoxLayout,
)
from PySide6.QtCore import Qt, QDate

from app.constants import CLASS_OPTIONS, PAYMENT_STATUS, UNASSIGNED_CLASS_LABEL
from app.models.student import Student, UNASSIGNED_CLASS
from app.services import student_service

_DATE_FORMAT = "dd/MM/yyyy"


def _make_date_edit() -> QDateEdit:
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat(_DATE_FORMAT)
    date_edit.setDate(QDate.currentDate())
    return date_edit


class StudentFormDialog(QDialog):
    def __init__(self, student: Student = None, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._student = student
        self._is_edit = student is not None
        self.setWindowTitle("تعديل بيانات الطالب" if self._is_edit else "إضافة طالب جديد")
        self.setMinimumWidth(400)

        self._build_ui()
        if student:
            self._fill_from(student)

    def _build_ui(self):
        outer = QVBoxLayout(self)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignRight)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        # --- اللقب / الإسم ---
        self.last_name_input = QLineEdit()
        self.last_name_input.setAlignment(Qt.AlignRight)
        form.addRow("اللقب *", self.last_name_input)

        self.first_name_input = QLineEdit()
        self.first_name_input.setAlignment(Qt.AlignRight)
        form.addRow("الإسم *", self.first_name_input)

        # --- الملف / الرمز ---
        self.file_number_input = QLineEdit()
        self.file_number_input.setAlignment(Qt.AlignRight)
        form.addRow("الملف", self.file_number_input)

        self.code_input = QLineEdit()
        self.code_input.setAlignment(Qt.AlignRight)
        form.addRow("الرمز", self.code_input)

        # --- الإزدياد / المكان ---
        self.birth_date_input = _make_date_edit()
        form.addRow("الإزدياد", self.birth_date_input)

        self.birth_place_input = QLineEdit()
        self.birth_place_input.setAlignment(Qt.AlignRight)
        form.addRow("المكان", self.birth_place_input)

        # --- تسجيل ---
        self.joined_input = _make_date_edit()
        form.addRow("تاريخ التسجيل", self.joined_input)

        # --- الولي / هاتف الولي ---
        self.guardian_input = QLineEdit()
        self.guardian_input.setAlignment(Qt.AlignRight)
        form.addRow("الولي *", self.guardian_input)

        self.guardian_phone_input = QLineEdit()
        self.guardian_phone_input.setAlignment(Qt.AlignRight)
        form.addRow("هاتف الولي", self.guardian_phone_input)

        # --- العنوان ---
        self.address_input = QLineEdit()
        self.address_input.setAlignment(Qt.AlignRight)
        form.addRow("العنوان", self.address_input)

        # --- الهاتف ---
        self.phone_input = QLineEdit()
        self.phone_input.setAlignment(Qt.AlignRight)
        self.phone_input.setPlaceholderText("0551 23 45 67")
        form.addRow("الهاتف *", self.phone_input)

        # --- المؤسسة التعليمية ---
        self.institution_input = QLineEdit()
        self.institution_input.setAlignment(Qt.AlignRight)
        form.addRow("المؤسسة التعليمية", self.institution_input)

        # --- القسم — edit mode only, assigned later, not at creation ---
        self.class_input = None
        if self._is_edit:
            self.class_input = QComboBox()
            self.class_input.addItem(UNASSIGNED_CLASS_LABEL, userData=UNASSIGNED_CLASS)
            self.class_input.addItems(CLASS_OPTIONS)
            form.addRow("القسم", self.class_input)

        # --- حالة الدفع ---
        self.status_input = QComboBox()
        for key, (label, _, _) in PAYMENT_STATUS.items():
            self.status_input.addItem(label, userData=key)
        form.addRow("حالة الدفع", self.status_input)

        outer.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

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