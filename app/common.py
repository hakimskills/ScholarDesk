# -*- coding: utf-8 -*-
"""
app/common.py

Small shared helpers used across pages and widgets so the same 3-6
line Qt boilerplate (label creation, button creation, shadow effects,
the scrollable-page skeleton) isn't repeated in every file.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


def make_label(text: str, object_name: str = "", align=Qt.AlignRight, style: str = "") -> QLabel:
    """Create a QLabel with the object name / alignment / style set in one call."""
    label = QLabel(text)
    if object_name:
        label.setObjectName(object_name)
    if align is not None:
        label.setAlignment(align)
    if style:
        label.setStyleSheet(style)
    return label


def make_button(text: str, object_name: str = "", on_click=None) -> QPushButton:
    """Create a QPushButton with object name, pointer cursor and click handler in one call."""
    btn = QPushButton(text)
    if object_name:
        btn.setObjectName(object_name)
    btn.setCursor(Qt.PointingHandCursor)
    if on_click is not None:
        btn.clicked.connect(on_click)
    return btn


def apply_shadow(widget: QWidget, blur=24, y_offset=8, alpha=18):
    """Attach the standard soft drop-shadow used on cards/sections."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(0)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(27, 33, 64, alpha))
    widget.setGraphicsEffect(shadow)


class ScrollPage(QWidget):
    """
    Base class for full pages made of a single RTL scroll area with a
    padded content column. Subclasses just push widgets/layouts into
    `self.content_layout` instead of rebuilding the scroll-area
    skeleton (root layout + QScrollArea + inner content widget) every
    time, which previously accounted for ~20 duplicated lines per page.
    """

    def __init__(self, margins=(28, 24, 28, 28), spacing=18, parent=None):
        super().__init__(parent)
        self.setObjectName("pageRoot")
        self.setLayoutDirection(Qt.RightToLeft)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setLayoutDirection(Qt.RightToLeft)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        content.setObjectName("scrollContent")
        content.setLayoutDirection(Qt.RightToLeft)

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(*margins)
        self.content_layout.setSpacing(spacing)

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)