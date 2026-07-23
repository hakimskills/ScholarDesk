# -*- coding: utf-8 -*-
"""
app/widgets/quick_action_button.py

A square-ish shortcut button used in the "Quick Actions" grid
(e.g. add student, take attendance, send SMS...). Emits the standard
QPushButton `clicked` signal so callers can hook it up to real logic
later without any changes to this widget.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


class QuickActionButton(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("quickAction")
        self.setText(f"{icon}\n{text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(78)
        self.setMinimumWidth(96)