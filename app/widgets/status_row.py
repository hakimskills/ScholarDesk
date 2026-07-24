# -*- coding: utf-8 -*-
"""
app/widgets/status_row.py

A labeled progress row used for "payment status" breakdowns
(e.g. Paid / Partial / Unpaid), each with its own color and count.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar

from app.common import make_label


class StatusRow(QWidget):
    def __init__(self, dot_color: str, label: str, count_text: str, percent: int, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        dot = make_label("●", align=None, style=f"color: {dot_color}; font-size: 12px;")
        dot.setFixedWidth(16)
        top_row.addWidget(dot)
        top_row.addWidget(make_label(label, "rowLabel", align=None))
        top_row.addStretch(1)
        top_row.addWidget(make_label(count_text, "rowValue", align=None))
        layout.addLayout(top_row)

        bar = QProgressBar(objectName="statusBar")
        bar.setRange(0, 100)
        bar.setValue(percent)
        bar.setTextVisible(False)
        bar.setStyleSheet(f"QProgressBar#statusBar::chunk {{ background-color: {dot_color}; }}")
        layout.addWidget(bar)