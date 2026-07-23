# -*- coding: utf-8 -*-
"""
app/widgets/stat_card.py

A KPI "stat" card used at the top of the dashboard: an icon badge,
a large value, a title and a small trend indicator (up/down vs. the
previous period). Fully reusable — just instantiate with new data.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.theme import Colors, Radius


class StatCard(QFrame):
    def __init__(
        self,
        icon: str,
        title: str,
        value: str,
        trend_text: str = "",
        trend_positive: bool = True,
        accent_color: str = Colors.PRIMARY,
        accent_bg: str = Colors.PRIMARY_LIGHT,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setMinimumHeight(140)
        self._build_ui(icon, title, value, trend_text, trend_positive, accent_color, accent_bg)
        self._apply_shadow()

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(27, 33, 64, 18))
        self.setGraphicsEffect(shadow)

    def _build_ui(self, icon, title, value, trend_text, trend_positive, accent_color, accent_bg):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(14)

        # Top row: icon badge
        top_row = QHBoxLayout()
        top_row.setSpacing(0)

        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setFixedSize(44, 44)
        icon_label.setStyleSheet(
            f"background-color: {accent_bg}; color: {accent_color};"
        )
        top_row.addWidget(icon_label)
        top_row.addStretch(1)
        outer.addLayout(top_row)

        # Value
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        outer.addWidget(value_label)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        outer.addWidget(title_label)

        # Trend row
        if trend_text:
            trend_row = QHBoxLayout()
            trend_row.setSpacing(8)

            badge = QLabel(("▲ " if trend_positive else "▼ ") + trend_text)
            badge.setObjectName("trendUp" if trend_positive else "trendDown")
            trend_row.addWidget(badge)

            caption = QLabel("مقارنة بالشهر الماضي")
            caption.setObjectName("trendCaption")
            trend_row.addWidget(caption)
            trend_row.addStretch(1)

            outer.addLayout(trend_row)
        else:
            outer.addStretch(1)