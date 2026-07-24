# -*- coding: utf-8 -*-
"""
app/constants.py

Small lookup tables shared between the students list page and the
add/edit student dialog, so both stay in sync automatically.
"""

from app.theme import Colors

# status_key -> (display label, text color, background color)
PAYMENT_STATUS = {
    "paid": ("مسدد", Colors.SUCCESS, Colors.SUCCESS_LIGHT),
    "unpaid": ("غير مسدد", Colors.DANGER, Colors.DANGER_LIGHT),
}
STATUS_LABEL_TO_KEY = {label: key for key, (label, _, _) in PAYMENT_STATUS.items()}

# Real class names only (no "all" option here — that's added separately
# by the filter combo on the students list page).
CLASS_OPTIONS = ["تحضيري", "السنة 1", "السنة 2", "السنة 3", "السنة 4", "السنة 5"]

# Shown wherever a student hasn't been assigned to a class yet — new
# students start this way; class is assigned later, not at creation.
UNASSIGNED_CLASS_LABEL = "غير محدد"