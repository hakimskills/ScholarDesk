import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.ui.dashboard import Dashboard


app = QApplication(sys.argv)

# Arabic RTL
app.setLayoutDirection(Qt.RightToLeft)

window = Dashboard()
window.setWindowTitle("نظام إدارة المدرسة")
window.resize(1200, 700)

window.show()

sys.exit(app.exec())