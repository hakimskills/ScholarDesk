# -*- coding: utf-8 -*-
"""
app/widgets/activity_item.py

A single row in the "Recent Activities" feed: a colored icon badge,
a title, a short meta description and a relative timestamp.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from app.theme import Colors


class ActivityItem(QFrame):
    def __init__(
        self,
        icon: str,
        title: str,
        meta: str,
        time_text: str,
        accent_color: str = Colors.PRIMARY,
        accent_bg: str = Colors.PRIMARY_LIGHT,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("activityItem")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setObjectName("activityIcon")
        icon_label.setFixedSize(38, 38)
        icon_label.setStyleSheet(f"background-color: {accent_bg}; color: {accent_color};")
        layout.addWidget(icon_label)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("activityTitle")
        title_label.setAlignment(Qt.AlignRight)
        text_box.addWidget(title_label)

        meta_label = QLabel(meta)
        meta_label.setObjectName("activityMeta")
        meta_label.setAlignment(Qt.AlignRight)
        text_box.addWidget(meta_label)

        layout.addLayout(text_box, 1)

        time_label = QLabel(time_text)
        time_label.setObjectName("activityTime")
        time_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(time_label)