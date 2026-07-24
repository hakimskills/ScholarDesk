# -*- coding: utf-8 -*-
"""
main.py

Application entry point. Sets up RTL layout direction, loads the
Arabic-friendly font, applies the global stylesheet, and hosts every
page inside a QStackedWidget so the Dashboard can navigate to them.
"""

import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt

from app.database import init_db
from app.services.student_service import seed_demo_data
from app.theme import load_app_fonts, build_app_font, build_stylesheet
from app.ui.dashboard import Dashboard
from app.ui.students import StudentsPage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المدرسة")
        self.resize(1360, 860)
        self.setMinimumSize(1100, 700)

        # Pages are added to a stack; each page's navigate_requested
        # signal tells us which one to show next. Add new pages/keys
        # here as they're built (classes, payments, attendance...).
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.dashboard = Dashboard()
        self.students_page = StudentsPage()

        self._pages = {
            "dashboard": self.dashboard,
            "students": self.students_page,
        }
        for page in self._pages.values():
            self.stack.addWidget(page)

        self.dashboard.navigate_requested.connect(self.go_to_page)
        self.students_page.navigate_requested.connect(self.go_to_page)

        self.go_to_page("dashboard")

    def go_to_page(self, page_key: str):
        page = self._pages.get(page_key)
        if page is not None:
            self.stack.setCurrentWidget(page)


def main():
    init_db()
    seed_demo_data()  # remove this line once you have real students in the table

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