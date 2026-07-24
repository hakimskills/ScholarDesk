# -*- coding: utf-8 -*-
"""
app/ui/dashboard.py

The main Dashboard page for the School Manager application.
Pure UI: all data below is realistic placeholder/sample data. Wire it
up to app/services + app/models once the SQLite layer is ready.
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QWidget
from PySide6.QtCore import Qt, Signal

from app.theme import Colors
from app.common import ScrollPage, make_label, make_button
from app.widgets import StatCard, SectionCard, ActivityItem, QuickActionButton

# (icon, title, value, accent_color, accent_bg, clickable)
_STATS = [
    ("🎓", "عدد الطلاب", "512", Colors.PRIMARY, Colors.PRIMARY_LIGHT, True),
    ("🧑‍🏫", "عدد الأساتذة", "34", Colors.INFO, Colors.INFO_LIGHT, False),
    ("📚", "عدد الأقسام", "24", Colors.VIOLET, Colors.VIOLET_LIGHT, False),
    ("💰", "مداخيل هذا الشهر", "486,000 دج", Colors.SUCCESS, Colors.SUCCESS_LIGHT, False),
]

# (icon, title, meta, time_text, accent_color, accent_bg)
_ACTIVITIES = [
    ("🧾", "تسديد دفعة", "الطالب: ياسين بلحاج — قسم السنة 3", "منذ 5 دقائق", Colors.SUCCESS, Colors.SUCCESS_LIGHT),
    ("👤", "تسجيل طالب جديد", "مريم عبد الرحمان — قسم تحضيري", "منذ 32 دقيقة", Colors.PRIMARY, Colors.PRIMARY_LIGHT),
    ("📋", "أخذ الحضور", "قسم السنة 5 — 28 من 30 حاضر", "منذ ساعة", Colors.INFO, Colors.INFO_LIGHT),
    ("✉️", "إرسال رسائل SMS", "تذكير بالدفع — 37 ولي أمر", "منذ 3 ساعات", Colors.VIOLET, Colors.VIOLET_LIGHT),
    ("⚠️", "تأخر في التسديد", "الطالب: عمر شريف — قسم السنة 2", "أمس، 18:40", Colors.DANGER, Colors.DANGER_LIGHT),
]

# (icon, label) — labels matching a page key below trigger navigation
_QUICK_ACTIONS = [
    ("👤", "إضافة طالب"),
    ("💳", "تسجيل دفعة"),
    ("📋", "أخذ الحضور"),
    ("✉️", "إرسال SMS"),
    ("📊", "إنشاء تقرير"),
    ("🏫", "إضافة قسم"),
]
_QUICK_ACTION_TARGETS = {"إضافة طالب": "students"}


class Dashboard(ScrollPage):
    """The dashboard / home page shown after login."""

    # Emitted with a page key ("students", "classes", "payments", ...)
    # whenever the user clicks something on the dashboard that should
    # switch pages. Connect this in MainWindow to a QStackedWidget.
    navigate_requested = Signal(str)

    def __init__(self, school_name: str = "مدرسة النجاح الخاصة", user_name: str = "عبد الله", parent=None):
        self.school_name = school_name
        self.user_name = user_name
        super().__init__(parent=parent)

        self.content_layout.addLayout(self._build_top_bar())
        self.content_layout.addLayout(self._build_stats_grid())
        self.content_layout.addLayout(self._build_main_grid())

    # ------------------------------------------------------------------ #
    # Top bar: greeting + search + quick actions
    # ------------------------------------------------------------------ #
    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(16)

        greeting_box = QVBoxLayout()
        greeting_box.setSpacing(4)
        greeting_box.addWidget(make_label(f"مرحباً بك، {self.user_name} 👋", "greetingTitle"))
        greeting_box.addWidget(make_label(f"إليك ملخص أداء {self.school_name} اليوم", "greetingSubtitle"))
        bar.addLayout(greeting_box)
        bar.addStretch(1)

        bar.addWidget(make_label("الخميس، 23 يوليو 2026", "dateLabel", align=None))

        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText("🔍  بحث عن طالب، قسم أو أستاذ...")
        search_box.setAlignment(Qt.AlignRight)
        search_box.setFixedWidth(240)
        bar.addWidget(search_box)

        bar.addWidget(make_button("🔔", "iconButton"))
        # Redirect trigger #1: top-bar CTA -> Students page
        bar.addWidget(make_button(
            "+  إضافة طالب جديد", "primaryButton",
            on_click=lambda: self.navigate_requested.emit("students"),
        ))
        return bar

    # ------------------------------------------------------------------ #
    # KPI grid: Students / Teachers / Classes / Income
    # ------------------------------------------------------------------ #
    def _build_stats_grid(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(18)

        for col, (icon, title, value, color, bg, clickable) in enumerate(_STATS):
            card = StatCard(icon=icon, title=title, value=value,
                             accent_color=color, accent_bg=bg, clickable=clickable)
            if clickable:
                # Redirect trigger #2: clicking the Students stat card -> Students page
                card.clicked.connect(lambda: self.navigate_requested.emit("students"))
            grid.addWidget(card, 0, col)
            grid.setColumnStretch(col, 1)
        return grid

    # ------------------------------------------------------------------ #
    # Main content grid: activities feed + quick actions
    # ------------------------------------------------------------------ #
    def _build_main_grid(self) -> QHBoxLayout:
        grid = QHBoxLayout()
        grid.setSpacing(18)

        main_col = QVBoxLayout()
        main_col.setSpacing(18)
        main_col.addWidget(self._build_activities_section())

        side_col = QVBoxLayout()
        side_col.setSpacing(18)
        side_col.addWidget(self._build_quick_actions_section())
        side_col.addStretch(1)

        main_wrap = QWidget()
        main_wrap.setLayout(main_col)

        side_wrap = QWidget()
        side_wrap.setLayout(side_col)
        side_wrap.setMaximumWidth(360)
        side_wrap.setMinimumWidth(320)

        grid.addWidget(main_wrap, 2)
        grid.addWidget(side_wrap, 1)
        return grid

    # ------------------------------------------------------------------ #
    # Recent activities feed
    # ------------------------------------------------------------------ #
    def _build_activities_section(self) -> SectionCard:
        section = SectionCard(title="آخر النشاطات", trailing=make_button("عرض الكل", "linkButton"))
        for icon, title, meta, time_text, color, bg in _ACTIVITIES:
            section.add_widget(ActivityItem(icon, title, meta, time_text, color, bg))
        return section

    # ------------------------------------------------------------------ #
    # Quick actions grid
    # ------------------------------------------------------------------ #
    def _build_quick_actions_section(self) -> SectionCard:
        section = SectionCard(title="إجراءات سريعة")

        grid = QGridLayout()
        grid.setSpacing(10)
        for index, (icon, label) in enumerate(_QUICK_ACTIONS):
            btn = QuickActionButton(icon, label)
            target = _QUICK_ACTION_TARGETS.get(label)
            if target:
                # Redirect trigger #3: "إضافة طالب" quick-action tile -> Students page
                btn.clicked.connect(lambda _=False, t=target: self.navigate_requested.emit(t))
            grid.addWidget(btn, *divmod(index, 3))

        section.add_layout(grid)
        return section