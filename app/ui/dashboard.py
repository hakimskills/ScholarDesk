# -*- coding: utf-8 -*-
"""
app/ui/dashboard.py

The Dashboard page: just a grid of big colored shortcut tiles — no
greeting bar, search box, stat cards, or activity feed.

Only "التلاميذ" is wired up today (-> the Students page), since
that's the only other page that exists yet. الأساتذة / الأفواج
الشهرية / جميع المتأخرين في الدفع each emit a page key nothing
currently maps to, so they're harmless no-ops until those pages are
built — add them to MainWindow's _pages dict in main.py when ready
and they'll start working with no changes needed here.
"""

from PySide6.QtWidgets import QGridLayout
from PySide6.QtCore import Signal

from app.common import ScrollPage
from app.widgets import MenuTile

# (icon, label, variant "accent"/"muted", target page key)
_TILES = [
    ("🧑‍🎓", "التلاميذ", "accent", "students"),
    ("🧑‍🏫", "الأساتذة", "muted", "teachers"),
    ("👥", "الأفواج الشهرية", "muted", "monthly_groups"),
    ("🏢", "جميع المتأخرين في الدفع", "accent", "late_payments"),
]

_TILE_COLUMNS = 2


class Dashboard(ScrollPage):
    """The dashboard / home page: a grid of navigation tiles."""

    # Emitted with a page key ("students", "groups", ...) whenever a
    # tile that maps to a real page is clicked. Connected in
    # MainWindow to a QStackedWidget.
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.content_layout.addLayout(self._build_tiles_grid())
        self.content_layout.addStretch(1)

    def _build_tiles_grid(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(18)

        for index, (icon, label, variant, target) in enumerate(_TILES):
            tile = MenuTile(icon, label, variant=variant)
            tile.clicked.connect(lambda _=False, t=target: self.navigate_requested.emit(t))
            row, col = divmod(index, _TILE_COLUMNS)
            grid.addWidget(tile, row, col)

        for col in range(_TILE_COLUMNS):
            grid.setColumnStretch(col, 1)
        return grid