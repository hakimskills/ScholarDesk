# -*- coding: utf-8 -*-
"""
app/widgets/status_row.py

A labeled progress row used for "payment status" breakdowns
(e.g. Paid / Partial / Unpaid), each with its own color and count.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

from app.theme import Colors


class StatusRow(QWidget):
    def __init__(self, dot_color: str, label: str, count_text: str, percent: int, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        top_row = QHBoxLayout()

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 12px;")
        dot.setFixedWidth(16)
        top_row.addWidget(dot)

        label_widget = QLabel(label)
        label_widget.setObjectName("rowLabel")
        top_row.addWidget(label_widget)
        top_row.addStretch(1)

        value_widget = QLabel(count_text)
        value_widget.setObjectName("rowValue")
        top_row.addWidget(value_widget)

        layout.addLayout(top_row)

        bar = QProgressBar()
        bar.setObjectName("statusBar")
        bar.setRange(0, 100)
        bar.setValue(percent)
        bar.setTextVisible(False)
        bar.setStyleSheet(f"QProgressBar#statusBar::chunk {{ background-color: {dot_color}; }}")
        layout.addWidget(bar)