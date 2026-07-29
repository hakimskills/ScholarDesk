# -*- coding: utf-8 -*-
"""
app/ui/group_students_dialog.py

"إدارة التلاميذ" — add/remove a group's students, opened by
right-clicking (or the ✏-adjacent action) a row in app/ui/groups.py.
Deliberately separate from app/ui/group_form.py: creating or editing
a group only ever touches the group's own fields; membership is
edited here instead, once the group already exists.

Two tabs, like a browser, instead of one combined checklist:
- "إضافة تلاميذ"  — every student NOT already in this group, with a
  search box and a "إضافة المحدد" button.
- "تلاميذ الفوج"  — every student already IN this group, with its
  own search box, a "حذف المحدد" button for multi-select removal,
  and a right-click "🗑 حذف تلميذ" action for removing just one.

Selecting a student is click-to-select, not a checkbox: clicking a
row darkens its background (hover darkens it a little, a genuine
selection darkens it further) and reveals a small "✕" on the left to
deselect — see _PickRow below.

Every add is written to the database immediately. Every REMOVE goes
through a confirmation warning first (_confirm_removal), whether it's
a single right-click delete or a multi-select "حذف المحدد" — once a
student's removed from a group there's no undo, so it's worth the
extra click. Both tabs refresh each other right away after either
kind of change, and the dialog only needs a single "إغلاق" button.

Styled with the same formDialog/formCard building blocks used by
app/ui/group_form.py so it reads as part of the same app rather than
a bolted-on picker.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QTabWidget,
    QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QMenu,
    QLabel, QPushButton, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from app.theme import Colors
from app.models.group import Group
from app.services import group_service
from app.common import make_label, make_button


def _make_search_box(placeholder: str) -> QLineEdit:
    box = QLineEdit(objectName="formInput")
    box.setLayoutDirection(Qt.RightToLeft)
    box.setAlignment(Qt.AlignRight)
    box.setPlaceholderText(placeholder)
    return box


class _PickRow(QFrame):
    """One student row in a pick list — click anywhere to select
    (darkens the background), click the "✕" (only visible once
    selected) to deselect. Replaces the old checkbox-per-item
    approach entirely."""

    toggled = Signal()

    def __init__(self, student_id: int, name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("pickRow")
        self.setProperty("selected", "false")
        self.student_id = student_id
        self._selected = False
        self.setCursor(Qt.PointingHandCursor)
        # Set explicitly rather than relying on inherited direction —
        # this widget is built with parent=None and only reparented
        # later (via setItemWidget), so it needs its own RTL setting
        # to lay out addWidget() calls in the right visual order.
        self.setLayoutDirection(Qt.RightToLeft)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(8)

        # Added first -> the leading (right) edge in RTL. Name reads
        # naturally on the right, the way Arabic text is expected to
        # sit in a row like this.
        self.name_label = QLabel(name)
        self.name_label.setObjectName("pickRowLabel")
        self.name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.name_label)

        layout.addStretch(1)

        # Added last -> the trailing (left) edge in RTL: the deselect
        # "✕", hidden until this row is actually selected.
        self.remove_button = QPushButton("✕")
        self.remove_button.setObjectName("pickRowRemove")
        self.remove_button.setFixedSize(20, 20)
        self.remove_button.setCursor(Qt.PointingHandCursor)
        self.remove_button.setVisible(False)
        self.remove_button.clicked.connect(self._deselect)
        layout.addWidget(self.remove_button, 0, Qt.AlignLeft)

    def is_selected(self) -> bool:
        return self._selected

    def set_selected(self, selected: bool):
        self._selected = selected
        self.setProperty("selected", "true" if selected else "false")
        self.remove_button.setVisible(selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def _deselect(self):
        self.set_selected(False)
        self.toggled.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_selected(not self._selected)
            self.toggled.emit()
        super().mousePressEvent(event)


def _make_pick_list() -> QListWidget:
    list_widget = QListWidget()
    list_widget.setObjectName("studentPickList")
    list_widget.setLayoutDirection(Qt.RightToLeft)
    list_widget.setMinimumHeight(280)
    # Selection is handled entirely by _PickRow's own click handling
    # (see above) — Qt's built-in row selection isn't used at all,
    # so it's turned off here to avoid a second, conflicting
    # highlight fighting with pickRow's own "selected" background.
    list_widget.setSelectionMode(QAbstractItemView.NoSelection)
    list_widget.setFocusPolicy(Qt.NoFocus)
    return list_widget


class GroupStudentsDialog(QDialog):
    """Add/remove students for one existing group."""

    def __init__(self, group: Group, parent=None):
        super().__init__(parent)
        self.setObjectName("formDialog")
        self.setLayoutDirection(Qt.RightToLeft)
        self._group = group
        self.setWindowTitle("إدارة تلاميذ الفوج")
        self.setMinimumWidth(500)

        self._build_ui()
        self._reload_add_tab()
        self._reload_members_tab()
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
        header.addWidget(make_label("إدارة تلاميذ الفوج", "formTitle", align=Qt.AlignRight))
        header.addWidget(make_label(
            self._group.display_name or "—", "formSubtitle", align=Qt.AlignRight,
        ))
        outer.addLayout(header)

        card = QFrame(objectName="formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        self.tabs.addTab(self._build_add_tab(), "إضافة تلاميذ")
        self.tabs.addTab(self._build_members_tab(), "تلاميذ الفوج")
        card_layout.addWidget(self.tabs)

        outer.addWidget(card, 1)
        outer.addLayout(self._build_buttons_row())

    def _fit_to_screen(self):
        screen = self.screen() or (self.parent().screen() if self.parent() else None)
        if screen is None:
            return
        available = screen.availableGeometry()
        max_height = max(460, int(available.height() * 0.85))
        self.resize(self.width(), min(self.sizeHint().height(), max_height))
        self.setMaximumHeight(max_height)

    def _build_buttons_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch(1)
        row.addWidget(make_button("إغلاق", "primaryButton", on_click=self.accept))
        return row

    # ------------------------------------------------------------------ #
    # Tab 1 — إضافة تلاميذ (students NOT in the group yet)
    # ------------------------------------------------------------------ #
    def _build_add_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 14, 4, 4)
        layout.setSpacing(12)

        self.add_search_input = _make_search_box("🔍  ابحث عن تلميذ لإضافته...")
        self.add_search_input.textChanged.connect(lambda text: self._filter_list(self.add_list, text))
        layout.addWidget(self.add_search_input)

        self.add_list = _make_pick_list()
        layout.addWidget(self.add_list, 1)

        footer = QHBoxLayout()
        self.add_count_label = make_label("", style="color: #6B7189; font-size: 11.5px;", align=Qt.AlignRight)
        footer.addWidget(self.add_count_label, 1)
        footer.addWidget(make_button("إضافة المحدد", "primaryButton", on_click=self._add_selected))
        layout.addLayout(footer)

        return tab

    def _reload_add_tab(self):
        self.add_list.clear()
        for student in group_service.get_students_not_in_group(self._group.id):
            self._add_pick_row(self.add_list, student.id, student.full_name)
        self.add_search_input.clear()
        self._update_add_count_label()

    def _update_add_count_label(self, *_):
        total = self.add_list.count()
        self.add_count_label.setText(
            f"{total} تلميذ متاح للإضافة" if total else "كل التلاميذ منضمّون لهذا الفوج بالفعل"
        )

    def _add_selected(self):
        selected_ids = self._selected_ids(self.add_list)
        if not selected_ids:
            return
        group_service.add_students_to_group(self._group.id, selected_ids)
        self._reload_add_tab()
        self._reload_members_tab()

    # ------------------------------------------------------------------ #
    # Tab 2 — تلاميذ الفوج (students already in the group)
    # ------------------------------------------------------------------ #
    def _build_members_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 14, 4, 4)
        layout.setSpacing(12)

        self.members_search_input = _make_search_box("🔍  ابحث عن تلميذ لحذفه...")
        self.members_search_input.textChanged.connect(lambda text: self._filter_list(self.members_list, text))
        layout.addWidget(self.members_search_input)

        self.members_list = _make_pick_list()
        self.members_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.members_list.customContextMenuRequested.connect(self._on_members_context_menu)
        layout.addWidget(self.members_list, 1)

        footer = QHBoxLayout()
        self.members_count_label = make_label("", style="color: #6B7189; font-size: 11.5px;", align=Qt.AlignRight)
        footer.addWidget(self.members_count_label, 1)
        footer.addWidget(make_button("حذف المحدد", "outlineButton", on_click=self._remove_selected))
        layout.addLayout(footer)

        return tab

    def _reload_members_tab(self):
        self.members_list.clear()
        for student in group_service.get_students_for_group(self._group.id):
            self._add_pick_row(self.members_list, student.id, student.full_name)
        self.members_search_input.clear()
        self._update_members_count_label()

    def _update_members_count_label(self, *_):
        total = self.members_list.count()
        self.members_count_label.setText(
            f"{total} تلميذ في هذا الفوج" if total else "لا يوجد تلاميذ في هذا الفوج بعد"
        )

    def _remove_selected(self):
        selected_ids = self._selected_ids(self.members_list)
        if not selected_ids:
            return
        if not self._confirm_removal(len(selected_ids)):
            return
        group_service.remove_students_from_group(self._group.id, selected_ids)
        self._reload_members_tab()
        self._reload_add_tab()

    def _on_members_context_menu(self, pos):
        item = self.members_list.itemAt(pos)
        if item is None:
            return
        row = self.members_list.itemWidget(item)
        if row is None:
            return

        menu = QMenu(self)
        menu.setLayoutDirection(Qt.RightToLeft)
        menu.addAction("🗑  حذف تلميذ", lambda: self._remove_one(row.student_id, row.name_label.text()))
        menu.exec(self.members_list.viewport().mapToGlobal(pos))

    def _remove_one(self, student_id: int, student_name: str = ""):
        if not self._confirm_removal(1, student_name):
            return
        group_service.remove_students_from_group(self._group.id, [student_id])
        self._reload_members_tab()
        self._reload_add_tab()

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #
    def _add_pick_row(self, list_widget: QListWidget, student_id: int, name: str):
        item = QListWidgetItem()
        row = _PickRow(student_id, name)
        item.setSizeHint(row.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, row)

    def _filter_list(self, list_widget: QListWidget, text: str):
        text = text.strip()
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            row = list_widget.itemWidget(item)
            item.setHidden(bool(text) and text not in row.name_label.text())

    def _selected_ids(self, list_widget: QListWidget):
        ids = []
        for i in range(list_widget.count()):
            row = list_widget.itemWidget(list_widget.item(i))
            if row is not None and row.is_selected():
                ids.append(row.student_id)
        return ids

    def _confirm_removal(self, count: int, student_name: str = "") -> bool:
        """Every removal — single or bulk — gets a real confirmation
        first; there's no undo once a student's off the roster."""
        if count == 1 and student_name:
            message = f"هل أنت متأكد من حذف {student_name} من هذا الفوج؟"
        else:
            message = f"هل أنت متأكد من حذف {count} تلميذ من هذا الفوج؟"

        box = QMessageBox(self)
        box.setWindowTitle("تأكيد الحذف")
        box.setText(message)
        box.setIcon(QMessageBox.Warning)
        box.setLayoutDirection(Qt.RightToLeft)
        # Belt-and-suspenders on top of theme.py's global QMessageBox
        # rule: an explicit background here guarantees this specific
        # popup never renders see-through, regardless of platform.
        box.setStyleSheet(f"QMessageBox {{ background-color: {Colors.SURFACE}; }}")

        yes_button = box.addButton("حذف", QMessageBox.YesRole)
        no_button = box.addButton("إلغاء", QMessageBox.NoRole)
        box.setDefaultButton(no_button)

        box.exec()
        return box.clickedButton() == yes_button