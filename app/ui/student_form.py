# -*- coding: utf-8 -*-
"""
app/ui/student_form.py

Add / edit student dialog. Pass an existing Student to prefill it in
edit mode; pass nothing to create a new one. Either way, saving talks
to app/services/student_service.py directly — the caller just needs
to refresh its table after the dialog closes with Accepted.
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDialogButtonBox, QMessageBox, QVBoxLayout,
)
from PySide6.QtCore import Qt, QDate

from app.constants import CLASS_OPTIONS, PAYMENT_STATUS
from app.models.student import Student
from app.services import student_service

_DATE_FORMAT = "dd/MM/yyyy"


class StudentFormDialog(QDialog):
    def __init__(self, student: Student = None, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._student = student
        self.setWindowTitle("تعديل بيانات الطالب" if student else "إضافة طالب جديد")
        self.setMinimumWidth(380)

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

        self.name_input = QLineEdit()
        self.name_input.setAlignment(Qt.AlignRight)
        form.addRow("الاسم الكامل *", self.name_input)

        self.class_input = QComboBox()
        self.class_input.addItems(CLASS_OPTIONS)
        form.addRow("القسم *", self.class_input)

        self.guardian_input = QLineEdit()
        self.guardian_input.setAlignment(Qt.AlignRight)
        form.addRow("ولي الأمر *", self.guardian_input)

        self.phone_input = QLineEdit()
        self.phone_input.setAlignment(Qt.AlignRight)
        self.phone_input.setPlaceholderText("0551 23 45 67")
        form.addRow("الهاتف *", self.phone_input)

        self.joined_input = QDateEdit()
        self.joined_input.setCalendarPopup(True)
        self.joined_input.setDisplayFormat(_DATE_FORMAT)
        self.joined_input.setDate(QDate.currentDate())
        form.addRow("تاريخ التسجيل", self.joined_input)

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
        self.name_input.setText(student.name)
        class_idx = self.class_input.findText(student.class_name)
        if class_idx >= 0:
            self.class_input.setCurrentIndex(class_idx)
        self.guardian_input.setText(student.guardian)
        self.phone_input.setText(student.phone)

        joined = QDate.fromString(student.joined_at, _DATE_FORMAT)
        if joined.isValid():
            self.joined_input.setDate(joined)

        status_idx = self.status_input.findData(student.payment_status)
        if status_idx >= 0:
            self.status_input.setCurrentIndex(status_idx)

    def _on_save(self):
        name = self.name_input.text().strip()
        guardian = self.guardian_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not guardian or not phone:
            QMessageBox.warning(self, "بيانات ناقصة", "الرجاء تعبئة الاسم وولي الأمر والهاتف.")
            return

        student = self._student or Student(name="", class_name="", guardian="", phone="", joined_at="")
        student.name = name
        student.class_name = self.class_input.currentText()
        student.guardian = guardian
        student.phone = phone
        student.joined_at = self.joined_input.date().toString(_DATE_FORMAT)
        student.payment_status = self.status_input.currentData()

        if student.id is None:
            student_service.create_student(student)
        else:
            student_service.update_student(student)

        self.accept()