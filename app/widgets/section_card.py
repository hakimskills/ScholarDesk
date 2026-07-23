# -*- coding: utf-8 -*-
"""
app/widgets/section_card.py

A generic "panel" container used everywhere on the dashboard (charts,
lists, quick actions...). Provides a consistent header with a title,
an optional subtitle, an optional trailing widget (buttons / chips)
and a body area that callers fill with their own content.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QColor


class SectionCard(QFrame):
    def __init__(self, title: str, subtitle: str = "", trailing: QWidget = None, parent=None):
        super().__init__(parent)
        self.setObjectName("sectionCard")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 20, 22, 20)
        outer.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(4)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        title_box.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("sectionSubtitle")
            title_box.addWidget(subtitle_label)

        header.addLayout(title_box)
        header.addStretch(1)

        if trailing is not None:
            header.addWidget(trailing)

        outer.addLayout(header)

        separator = QFrame()
        separator.setObjectName("sectionSeparator")
        separator.setFrameShape(QFrame.HLine)
        outer.addWidget(separator)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(12)
        outer.addWidget(self.body)

        self._apply_shadow()

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(27, 33, 64, 16))
        self.setGraphicsEffect(shadow)

    def add_widget(self, widget: QWidget):
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        self.body_layout.addLayout(layout)