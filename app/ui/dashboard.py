# -*- coding: utf-8 -*-
"""
app/ui/dashboard.py

The Dashboard page: a grid of compact, rectangular shortcut tiles —
no greeting bar, search box, stat cards, or activity feed.

Tiles are either:
- ready=True   -> primary-colored, navigates to a real page.
- ready=False  -> grey with a "قريباً" badge, and does nothing when
  clicked — that feature hasn't been built yet.

التلاميذ / الأساتذة / الأفواج / الرسائل are wired to real pages
today (see main.py's _pages dict). Everything else is a placeholder:
add its page to _pages and flip its `ready` flag to True here when
it's built — nothing else needs to change.
"""

from PySide6.QtWidgets import QGridLayout
from PySide6.QtCore import Signal

from app.common import ScrollPage
from app.widgets import MenuTile

# (icon, label, ready, target page key)
_TILES = [
    ("🧑‍🎓", "التلاميذ", True, "students"),
    ("🧑‍🏫", "الأساتذة", True, "teachers"),
    ("👥", "الأفواج", True, "monthly_groups"),
    ("📋", "الغيابات", False, "attendance"),
    ("💳", "المدفوعات", False, "payments"),
    ("✉️", "الرسائل", True, "messages"),
    ("📊", "التقارير", False, "reports"),
    ("⚙️", "الإعدادات", False, "settings"),
]

_TILE_COLUMNS = 4


class Dashboard(ScrollPage):
    """The dashboard / home page: a grid of navigation tiles."""

    # Emitted with a page key ("students", "teachers", ...) whenever
    # a *ready* tile is clicked. Connected in MainWindow to a
    # QStackedWidget. Coming-soon tiles never emit this at all.
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.content_layout.addLayout(self._build_tiles_grid())
        self.content_layout.addStretch(1)

    def _build_tiles_grid(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(12)

        for index, (icon, label, ready, target) in enumerate(_TILES):
            tile = MenuTile(icon, label, ready=ready)
            tile.clicked.connect(lambda _=False, t=target: self.navigate_requested.emit(t))
            row, col = divmod(index, _TILE_COLUMNS)
            grid.addWidget(tile, row, col)

        for col in range(_TILE_COLUMNS):
            grid.setColumnStretch(col, 1)
        return grid