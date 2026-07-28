# -*- coding: utf-8 -*-
"""
app/widgets/menu_tile.py

A compact, rectangular dashboard shortcut tile — deliberately NOT a
rounded pill, so a full grid of these reads as a dense toolbar rather
than a row of big buttons. Two states, not colors:

- ready=True  -> primary-colored, clickable, navigates immediately.
- ready=False -> grey, shows a small "قريباً" badge, and does
  nothing when clicked — the feature just hasn't been built yet.

Styled in app/theme.py under QFrame#menuTile[variant="ready"/"soon"].
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class MenuTile(QFrame):
    clicked = Signal()

    def __init__(self, icon: str, label: str, ready: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("menuTile")
        self.setProperty("variant", "ready" if ready else "soon")
        self._ready = ready
        self.setFixedHeight(64)
        self.setCursor(Qt.PointingHandCursor if ready else Qt.ArrowCursor)
        if not ready:
            self.setToolTip("قريباً")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(1)

        icon_label = QLabel(icon)
        icon_label.setObjectName("menuTileIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        text_label = QLabel(label)
        text_label.setObjectName("menuTileLabel")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label, 1)

        if not ready:
            badge = QLabel("قريباً")
            badge.setObjectName("menuTileBadge")
            badge.setAlignment(Qt.AlignCenter)
            layout.addWidget(badge, 0, Qt.AlignHCenter)

    def mousePressEvent(self, event):
        if self._ready and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)