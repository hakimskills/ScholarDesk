# -*- coding: utf-8 -*-
"""
app/widgets/menu_tile.py

A big, colored dashboard shortcut button (the "الغيابات / تلميذ /
جميع التلاميذ..." tiles). Two visual variants only — "accent" (teal,
for the handful of highlighted actions) and "muted" (the slate-blue
default) — set via the `variant` constructor arg, styled in
app/theme.py under QPushButton#menuTile[variant=...].
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


class MenuTile(QPushButton):
    def __init__(self, icon: str, label: str, variant: str = "muted", parent=None):
        super().__init__(parent)
        self.setObjectName("menuTile")
        self.setProperty("variant", variant)
        self.setText(f"{icon}   {label}" if icon else label)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(96)