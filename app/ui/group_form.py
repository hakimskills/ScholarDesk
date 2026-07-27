# -*- coding: utf-8 -*-
"""
app/ui/group_form.py

Add / edit فوج (class/group) dialog — fields mirror the reference
form: المستوى (free text), المادة (free text), الفوج (a fixed
section-letter dropdown, e.g. "A"), عدد الحصص/الجولة, المدة (سا),
الأستاذ (with the same "+" quick-add-teacher shortcut shown in the
photo), مبلغ التلميذ, مدفوعات الأستاذ بالنسبة المئوية, مبلغ
الأستاذ/تلميذ (with a live النسبة = ...% readout), الفرع, الملاحظة —
plus a student picker, since a group holds MANY students (unlike the
teacher field, which holds exactly one).

The class's own display name isn't a separate field — it's always
المستوى + المادة + الفوج, in that order (e.g. "3 ابتدائي رياضيات A"),
computed by Group.display_name and previewed live as you type/pick.

Styled via the same formDialog/formCard/formInput rules in
app/theme.py used by student_form.py / teacher_form.py, including
the scrollable body so the buttons stay reachable on a short screen.

Saving talks to app/services/group_service.py directly — the caller
just needs to refresh its table after the dialog closes with
Accepted.
"""

from PySide6.QtWidgets import (
    QDialog, QGridLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QListWidget, QListWidgetItem, QMessageBox, QVBoxLayout,
    QHBoxLayout, QFrame, QWidget, QLabel, QScrollArea,
)
from PySide6.QtCore import Qt

from app.constants import SECTION_OPTIONS
from app.models.group import Group
from app.services import group_service, teacher_service, student_service
from app.common import make_label, make_button
from app.ui.teacher_form import TeacherFormDialog

_UNSET = ""  # dropdown placeholder value, shown as "-"
_CURRENCY_SUFFIX = " دج"


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


def _make_amount_spin() -> QDoubleSpinBox:
    spin = QDoubleSpinBox(objectName="formInput")
    spin.setRange(0, 10_000_000)
    spin.setDecimals(0)
    spin.setSingleStep(100)
    spin.setSuffix(_CURRENCY_SUFFIX)
    spin.setAlignment(Qt.AlignRight)
    return spin


def _field_box(label_text: str, widget: QWidget) -> QVBoxLayout:
    """Label stacked above its input — one cell of the two-column grid."""
    box = QVBoxLayout()
    box.setSpacing(6)
    box.addWidget(make_label(label_text, "formFieldLabel", align=Qt.AlignRight))
    box.addWidget(widget)
    return box


class GroupFormDialog(QDialog):
    def __init__(self, group: Group = None, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._group = group
        self._is_edit = group is not None
        self.setWindowTitle("تعديل الفوج" if self._is_edit else "إضافة فوج جديد")
        self.setMinimumWidth(620)

        self._build_ui()
        if group:
            self._fill_from(group)
        self._update_percentage_label()
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

        card_layout.addLayout(self._build_group_section())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_teacher_payment_section())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_students_section())
        card_layout.addWidget(self._separator())
        card_layout.addLayout(self._build_notes_section())

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
        max_height = max(480, int(available.height() * 0.9))
        self.resize(self.width(), min(self.sizeHint().height(), max_height))
        self.setMaximumHeight(max_height)

    def _build_header(self) -> QVBoxLayout:
        header = QVBoxLayout()
        header.setSpacing(2)
        title = "تعديل الفوج" if self._is_edit else "إضافة فوج جديد"
        subtitle = "عدّل بيانات الفوج، الأستاذ والتلاميذ." if self._is_edit else "أدخل بيانات الفوج، وحدّد الأستاذ والتلاميذ."
        header.addWidget(make_label(title, "formTitle", align=Qt.AlignRight))
        header.addWidget(make_label(subtitle, "formSubtitle", align=Qt.AlignRight))
        return header

    def _separator(self) -> QFrame:
        line = QFrame(objectName="formHeaderSeparator")
        line.setFrameShape(QFrame.HLine)
        return line

    def _section_title(self, text: str) -> QLabel:
        return make_label(text, "formSectionTitle", align=Qt.AlignRight)

    # --- معلومات الفوج ---
    def _build_group_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("معلومات الفوج"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        # المستوى and المادة are free text — schools name levels and
        # subjects however they want (e.g. "3 ابتدائي"), there's no
        # fixed list for either. الفوج is the one fixed-list part:
        # a letter. The three combine, in this order, into the
        # class's full name (see _update_name_preview).
        self.level_input = _make_line_edit("مثال: 3 ابتدائي")
        self.subject_input = _make_line_edit("مثال: رياضيات")
        self.section_input = _make_combo(SECTION_OPTIONS)

        self.level_input.textChanged.connect(self._update_name_preview)
        self.subject_input.textChanged.connect(self._update_name_preview)
        self.section_input.currentIndexChanged.connect(self._update_name_preview)

        self.sessions_input = QSpinBox(objectName="formInput")
        self.sessions_input.setRange(0, 100)
        self.sessions_input.setValue(4)
        self.sessions_input.setAlignment(Qt.AlignRight)

        self.duration_input = QDoubleSpinBox(objectName="formInput")
        self.duration_input.setRange(0, 24)
        self.duration_input.setSingleStep(0.5)
        self.duration_input.setValue(2)
        self.duration_input.setSuffix(" سا")
        self.duration_input.setAlignment(Qt.AlignRight)

        self.branch_input = _make_line_edit()

        grid.addLayout(_field_box("المستوى *", self.level_input), 0, 0)
        grid.addLayout(_field_box("المادة *", self.subject_input), 0, 1)
        grid.addLayout(_field_box("الفوج *", self.section_input), 1, 0)
        grid.addLayout(_field_box("عدد الحصص/الجولة", self.sessions_input), 1, 1)
        grid.addLayout(_field_box("المدة (سا)", self.duration_input), 2, 0)
        grid.addLayout(_field_box("الفرع", self.branch_input), 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        section.addLayout(grid)

        self.name_preview_label = make_label(
            "اسم الفوج: —", style="color: #4F5FF0; font-weight: 700;", align=Qt.AlignRight,
        )
        section.addWidget(self.name_preview_label)

        return section

    def _update_name_preview(self, *_):
        preview = Group(
            level=self.level_input.text().strip(),
            subject=self.subject_input.text().strip(),
            section=self.section_input.currentData() or "",
        ).display_name
        self.name_preview_label.setText(f"اسم الفوج: {preview}" if preview else "اسم الفوج: —")

    # --- الأستاذ والمدفوعات ---
    def _build_teacher_payment_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("الأستاذ والمدفوعات"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        # الأستاذ combo + the same "+" quick-add button shown in the photo.
        self.teacher_input = QComboBox(objectName="formCombo")
        self._reload_teachers()
        teacher_row = QHBoxLayout()
        teacher_row.setSpacing(8)
        teacher_row.addWidget(self.teacher_input, 1)
        teacher_row.addWidget(make_button("+", "outlineButton", on_click=self._add_teacher_inline))
        teacher_field = QVBoxLayout()
        teacher_field.setSpacing(6)
        teacher_field.addWidget(make_label("الأستاذ (واحد لكل فوج)", "formFieldLabel", align=Qt.AlignRight))
        teacher_field.addLayout(teacher_row)

        self.student_amount_input = _make_amount_spin()

        self.percentage_mode_input = QCheckBox("مدفوعات الأستاذ بالنسبة المئوية")

        self.teacher_student_amount_input = _make_amount_spin()
        self.teacher_student_amount_input.valueChanged.connect(self._update_percentage_label)
        self.student_amount_input.valueChanged.connect(self._update_percentage_label)

        self.percentage_label = make_label("النسبة = —", style="color: #F1506E; font-weight: 700;")

        grid.addLayout(teacher_field, 0, 0)
        grid.addLayout(_field_box("مبلغ التلميذ", self.student_amount_input), 0, 1)
        grid.addWidget(self.percentage_mode_input, 1, 0)
        grid.addLayout(_field_box("مبلغ الأستاذ/تلميذ", self.teacher_student_amount_input), 1, 1)
        grid.addWidget(self.percentage_label, 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        section.addLayout(grid)
        return section

    def _reload_teachers(self, select_id: int = None):
        self.teacher_input.blockSignals(True)
        self.teacher_input.clear()
        self.teacher_input.addItem("-", userData=None)
        for teacher in teacher_service.get_all_teachers():
            self.teacher_input.addItem(teacher.full_name, userData=teacher.id)
        if select_id is not None:
            idx = self.teacher_input.findData(select_id)
            self.teacher_input.setCurrentIndex(max(idx, 0))
        self.teacher_input.blockSignals(False)

    def _add_teacher_inline(self):
        dialog = TeacherFormDialog(parent=self)
        if dialog.exec() == TeacherFormDialog.Accepted:
            new_teacher_id = dialog._teacher.id if dialog._teacher else None
            self._reload_teachers(select_id=new_teacher_id)

    def _update_percentage_label(self):
        student_amount = self.student_amount_input.value()
        teacher_amount = self.teacher_student_amount_input.value()
        if student_amount and teacher_amount:
            pct = round((teacher_amount / student_amount) * 100, 1)
            self.percentage_label.setText(f"النسبة = {pct}%")
        else:
            self.percentage_label.setText("النسبة = —")

    # --- التلاميذ (فوج واحد يضم عدة تلاميذ) ---
    def _build_students_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(10)
        section.addWidget(self._section_title("التلاميذ"))

        self.student_search_input = _make_line_edit("🔍  ابحث عن تلميذ لإضافته...")
        self.student_search_input.textChanged.connect(self._filter_student_list)
        section.addWidget(self.student_search_input)

        self.student_list = QListWidget()
        self.student_list.setLayoutDirection(Qt.RightToLeft)
        self.student_list.setMaximumHeight(180)
        self._all_students = student_service.get_all_students()
        for student in self._all_students:
            item = QListWidgetItem(student.full_name)
            item.setData(Qt.UserRole, student.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.student_list.addItem(item)
        self.student_list.itemChanged.connect(self._update_students_count_label)
        section.addWidget(self.student_list)

        self.students_count_label = make_label("لم يتم اختيار أي تلميذ بعد", style="color: #6B7189; font-size: 11.5px;")
        section.addWidget(self.students_count_label)

        return section

    def _filter_student_list(self, text: str):
        text = text.strip()
        for row in range(self.student_list.count()):
            item = self.student_list.item(row)
            item.setHidden(bool(text) and text not in item.text())

    def _update_students_count_label(self, *_):
        count = sum(
            1 for row in range(self.student_list.count())
            if self.student_list.item(row).checkState() == Qt.Checked
        )
        self.students_count_label.setText(
            f"{count} تلميذ مختار" if count else "لم يتم اختيار أي تلميذ بعد"
        )

    def _selected_student_ids(self):
        return [
            self.student_list.item(row).data(Qt.UserRole)
            for row in range(self.student_list.count())
            if self.student_list.item(row).checkState() == Qt.Checked
        ]

    # --- الملاحظة ---
    def _build_notes_section(self) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(14)
        section.addWidget(self._section_title("ملاحظات"))

        self.note_input = _make_line_edit()
        section.addLayout(_field_box("الملاحظة", self.note_input))
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
    def _fill_from(self, group: Group):
        self.level_input.setText(group.level)
        self.subject_input.setText(group.subject)
        section_idx = self.section_input.findData(group.section)
        self.section_input.setCurrentIndex(max(section_idx, 0))
        self.sessions_input.setValue(group.sessions_per_round)
        self.duration_input.setValue(group.duration_hours)
        self.branch_input.setText(group.branch)

        if group.teacher_id is not None:
            idx = self.teacher_input.findData(group.teacher_id)
            self.teacher_input.setCurrentIndex(max(idx, 0))

        self.student_amount_input.setValue(group.student_amount)
        self.percentage_mode_input.setChecked(group.teacher_pay_by_percentage)
        self.teacher_student_amount_input.setValue(group.teacher_student_amount)
        self.note_input.setText(group.note)

        if group.id is not None:
            member_ids = set(group_service.get_group_student_ids(group.id))
            for row in range(self.student_list.count()):
                item = self.student_list.item(row)
                if item.data(Qt.UserRole) in member_ids:
                    item.setCheckState(Qt.Checked)
            self._update_students_count_label()

        self._update_name_preview()

    def _on_save(self):
        level = self.level_input.text().strip()
        section = self.section_input.currentData() or ""

        if not level or not section:
            QMessageBox.warning(self, "بيانات ناقصة", "الرجاء إدخال المستوى واختيار الفوج (A, B, C...).")
            return

        group = self._group or Group()
        group.level = level
        group.subject = self.subject_input.text().strip()
        group.section = section
        group.sessions_per_round = self.sessions_input.value()
        group.duration_hours = self.duration_input.value()
        group.teacher_id = self.teacher_input.currentData()
        group.student_amount = self.student_amount_input.value()
        group.teacher_pay_by_percentage = self.percentage_mode_input.isChecked()
        group.teacher_student_amount = self.teacher_student_amount_input.value()
        group.branch = self.branch_input.text().strip()
        group.note = self.note_input.text().strip()

        student_ids = self._selected_student_ids()
        if group.id is None:
            group_service.create_group(group, student_ids=student_ids)
        else:
            group_service.update_group(group, student_ids=student_ids)

        self._group = group
        self.accept()