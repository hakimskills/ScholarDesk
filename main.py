# -*- coding: utf-8 -*-
"""
main.py

Application entry point. Sets up RTL layout direction, loads the
Arabic-friendly font, applies the global stylesheet, and hosts every
page inside a QTabWidget — browser-style:

- "الرئيسية" (the dashboard) is the permanent first tab. It has no
  close button and can't be closed by any route (see
  _lock_dashboard_tab and the guard in _on_tab_close_requested).
- Clicking a tile on the dashboard opens that page as a NEW tab,
  which the person can close whenever they want. Clicking a tile (or
  a page's own "→ رجوع للوحة التحكم" button) for a page that's
  already open just switches to its existing tab instead of opening
  a duplicate.
- Closing a tab does not destroy the page's widget or its state
  (search text, filters, etc.) — it's simply removed from the tab
  bar and stays cached in self._pages, so reopening it later shows
  exactly where it was left.
"""

import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QTabBar
from PySide6.QtCore import Qt

from app.database import init_db
from app.theme import load_app_fonts, build_app_font, build_stylesheet
from app.ui.dashboard import Dashboard
from app.ui.students import StudentsPage
from app.ui.teachers import TeachersPage
from app.ui.groups import GroupsPage
from app.ui.messages import MessagesPage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

_DASHBOARD_TAB_INDEX = 0

# page key -> tab title. Add an entry here (and to MainWindow's
# _pages dict below) whenever a new page is built and its dashboard
# tile's `ready` flag flips to True.
_PAGE_TITLES = {
    "students": "🧑‍🎓  الطلاب",
    "teachers": "🧑‍🏫  الأساتذة",
    "monthly_groups": "👥  الأفواج",
    "messages": "✉️  الرسائل",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المدرسة")
        self.resize(1360, 860)
        self.setMinimumSize(1100, 700)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.tabBar().setObjectName("mainTabBar")
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(False)
        self.tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self.setCentralWidget(self.tabs)

        self.dashboard = Dashboard()
        self.students_page = StudentsPage()
        self.teachers_page = TeachersPage()
        self.groups_page = GroupsPage()
        self.messages_page = MessagesPage()

        # Every openable page besides the dashboard itself. Keyed the
        # same way dashboard tiles/back-buttons already emit.
        self._pages = {
            "students": self.students_page,
            "teachers": self.teachers_page,
            "monthly_groups": self.groups_page,
            "messages": self.messages_page,
        }

        self.dashboard.navigate_requested.connect(self.go_to_page)
        for page in self._pages.values():
            page.navigate_requested.connect(self.go_to_page)

        # Dashboard is always tab 0 and is added once, up front — it
        # is never opened/closed through go_to_page like the others.
        self.tabs.addTab(self.dashboard, "🏠  الرئيسية")
        self._lock_dashboard_tab()

    def _lock_dashboard_tab(self):
        """Remove the close button from the dashboard tab specifically
        — every tab opened afterwards keeps its close button; only
        this one is pinned."""
        tab_bar = self.tabs.tabBar()
        for side in (QTabBar.LeftSide, QTabBar.RightSide):
            button = tab_bar.tabButton(_DASHBOARD_TAB_INDEX, side)
            if button is not None:
                button.deleteLater()
                tab_bar.setTabButton(_DASHBOARD_TAB_INDEX, side, None)

    def go_to_page(self, page_key: str):
        if page_key == "dashboard":
            self.tabs.setCurrentIndex(_DASHBOARD_TAB_INDEX)
            return

        page = self._pages.get(page_key)
        if page is None:
            return  # a coming-soon tile with nowhere to go yet

        index = self.tabs.indexOf(page)
        if index == -1:
            title = _PAGE_TITLES.get(page_key, page_key)
            index = self.tabs.addTab(page, title)
        self.tabs.setCurrentIndex(index)

    def _on_tab_close_requested(self, index: int):
        if index == _DASHBOARD_TAB_INDEX:
            return  # belt-and-suspenders: the dashboard has no close
                     # button anyway, but this blocks any other route
                     # to closing it (e.g. a future keyboard shortcut).
        self.tabs.removeTab(index)


def main():
    init_db()  # creates data/school.db and the students/teachers tables on first run only

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    font_family = load_app_fonts(ASSETS_DIR)
    app.setFont(build_app_font(font_family, 10))
    app.setStyleSheet(build_stylesheet(font_family))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()