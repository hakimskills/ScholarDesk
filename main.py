# -*- coding: utf-8 -*-
"""
main.py

Application entry point. Sets up RTL layout direction, loads the
Arabic-friendly font, applies the global stylesheet and shows the
Dashboard page.
"""

import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt

from app.theme import load_app_fonts, build_app_font, build_stylesheet
from app.ui.dashboard import Dashboard

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المدرسة - لوحة التحكم")
        self.resize(1360, 860)
        self.setMinimumSize(1100, 700)
        self.setCentralWidget(Dashboard())


def main():
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