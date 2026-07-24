# -*- coding: utf-8 -*-
"""
app/widgets/activity_item.py

A single row in the "Recent Activities" feed: a colored icon badge,
a title, a short meta description and a relative timestamp.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt

from app.theme import Colors
from app.common import make_label


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

        icon_label = make_label(icon, "activityIcon", align=None,
                                 style=f"background-color: {accent_bg}; color: {accent_color};")
        icon_label.setFixedSize(38, 38)
        layout.addWidget(icon_label)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        text_box.addWidget(make_label(title, "activityTitle"))
        text_box.addWidget(make_label(meta, "activityMeta"))
        layout.addLayout(text_box, 1)

        layout.addWidget(make_label(time_text, "activityTime", align=Qt.AlignLeft | Qt.AlignTop))