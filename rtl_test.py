# -*- coding: utf-8 -*-
"""
rtl_test.py

Standalone diagnostic — run this directly with:
    python rtl_test.py

It does NOT import anything from your app/ folder, so there's no
cache, no shadowing, no theme.py stylesheet involved. It builds the
exact same kind of widgets student_form.py does (a title QLabel with
setAlignment(Qt.AlignRight) + setLayoutDirection(Qt.RightToLeft),
and a QVBoxLayout stacking them), with a visible colored border so
you can see exactly where each label's bounding box is.

WHAT TO LOOK FOR:
- If the text hugs the RIGHT edge of each colored box -> your Qt/
  PySide6 installation handles this correctly, which means the bug
  is that your real app isn't running the code you're editing
  (stale __pycache__, a duplicate file, or running from the wrong
  folder).
- If the text hugs the LEFT edge here too, in this completely
  isolated script -> it's an environment/Qt-version issue, not
  anything in student_form.py's code, and no further edits to that
  file will fix it on their own.
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

app = QApplication(sys.argv)
app.setLayoutDirection(Qt.RightToLeft)

window = QWidget()
window.setWindowTitle("RTL Diagnostic")
window.setLayoutDirection(Qt.RightToLeft)
window.resize(500, 300)

layout = QVBoxLayout(window)
layout.setContentsMargins(20, 20, 20, 20)
layout.setSpacing(16)

def make_test_label(text, bg_color):
    label = QLabel(text)
    label.setLayoutDirection(Qt.RightToLeft)
    label.setAlignment(Qt.AlignRight)
    label.setStyleSheet(f"background-color: {bg_color}; padding: 10px; font-size: 16px;")
    return label

layout.addWidget(make_test_label("إضافة طالب جديد (title)", "#FFD966"))
layout.addWidget(make_test_label("المعلومات الشخصية (section)", "#A9D18E"))
layout.addWidget(make_test_label("اللقب * (field label)", "#9DC3E6"))

info = QLabel(f"PySide6 app.layoutDirection() = {app.layoutDirection()}")
info.setStyleSheet("padding: 10px; color: #555;")
layout.addWidget(info)

window.show()
sys.exit(app.exec())