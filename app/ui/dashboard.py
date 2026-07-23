# -*- coding: utf-8 -*-
"""
app/ui/dashboard.py

The main Dashboard page for the School Manager application.
Pure UI: all data below is realistic placeholder/sample data. Wire it
up to app/services + app/models once the SQLite layer is ready.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal

from app.theme import Colors
from app.widgets import (
    StatCard,
    SectionCard,
    ActivityItem,
    QuickActionButton,
)


class Dashboard(QWidget):
    """The dashboard / home page shown after login."""

    # Emitted with a page key ("students", "classes", "payments", ...)
    # whenever the user clicks something on the dashboard that should
    # switch pages. Connect this in MainWindow to a QStackedWidget.
    navigate_requested = Signal(str)

    def __init__(self, school_name: str = "مدرسة النجاح الخاصة", user_name: str = "عبد الله", parent=None):
        super().__init__(parent)
        self.school_name = school_name
        self.user_name = user_name
        self.setObjectName("pageRoot")
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setLayoutDirection(Qt.RightToLeft)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        content.setObjectName("scrollContent")
        content.setLayoutDirection(Qt.RightToLeft)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 28)
        content_layout.setSpacing(22)

        content_layout.addLayout(self._build_top_bar())
        content_layout.addLayout(self._build_stats_grid())
        content_layout.addLayout(self._build_main_grid())

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)

    # ------------------------------------------------------------------ #
    # Top bar: greeting + search + quick actions
    # ------------------------------------------------------------------ #
    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(16)

        greeting_box = QVBoxLayout()
        greeting_box.setSpacing(4)

        title = QLabel(f"مرحباً بك، {self.user_name} 👋")
        title.setObjectName("greetingTitle")
        title.setAlignment(Qt.AlignRight)
        greeting_box.addWidget(title)

        subtitle = QLabel(f"إليك ملخص أداء {self.school_name} اليوم")
        subtitle.setObjectName("greetingSubtitle")
        subtitle.setAlignment(Qt.AlignRight)
        greeting_box.addWidget(subtitle)

        bar.addLayout(greeting_box)
        bar.addStretch(1)

        date_label = QLabel("الخميس، 23 يوليو 2026")
        date_label.setObjectName("dateLabel")
        bar.addWidget(date_label)

        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText("🔍  بحث عن طالب، قسم أو أستاذ...")
        search_box.setAlignment(Qt.AlignRight)
        search_box.setFixedWidth(240)
        bar.addWidget(search_box)

        bell_btn = QPushButton("🔔")
        bell_btn.setObjectName("iconButton")
        bell_btn.setCursor(Qt.PointingHandCursor)
        bar.addWidget(bell_btn)

        add_student_btn = QPushButton("+  إضافة طالب جديد")
        add_student_btn.setObjectName("primaryButton")
        add_student_btn.setCursor(Qt.PointingHandCursor)
        # Redirect trigger #1: top-bar CTA -> Students page
        add_student_btn.clicked.connect(lambda: self.navigate_requested.emit("students"))
        bar.addWidget(add_student_btn)

        return bar

    # ------------------------------------------------------------------ #
    # KPI grid: Students / Teachers / Classes / Income
    # ------------------------------------------------------------------ #
    def _build_stats_grid(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(18)

        students_card = StatCard(
            icon="🎓",
            title="عدد الطلاب",
            value="512",
            accent_color=Colors.PRIMARY,
            accent_bg=Colors.PRIMARY_LIGHT,
            clickable=True,
        )
        # Redirect trigger #2: clicking the Students stat card -> Students page
        students_card.clicked.connect(lambda: self.navigate_requested.emit("students"))

        teachers_card = StatCard(
            icon="🧑‍🏫",
            title="عدد الأساتذة",
            value="34",
            accent_color=Colors.INFO,
            accent_bg=Colors.INFO_LIGHT,
        )
        classes_card = StatCard(
            icon="📚",
            title="عدد الأقسام",
            value="24",
            accent_color=Colors.VIOLET,
            accent_bg=Colors.VIOLET_LIGHT,
        )
        income_card = StatCard(
            icon="💰",
            title="مداخيل هذا الشهر",
            value="486,000 دج",
            accent_color=Colors.SUCCESS,
            accent_bg=Colors.SUCCESS_LIGHT,
        )

        cards = [students_card, teachers_card, classes_card, income_card]
        for index, card in enumerate(cards):
            grid.addWidget(card, 0, index)

        for col in range(len(cards)):
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
        see_all = QPushButton("عرض الكل")
        see_all.setObjectName("linkButton")
        see_all.setCursor(Qt.PointingHandCursor)

        section = SectionCard(title="آخر النشاطات", trailing=see_all)

        activities = [
            ("🧾", "تسديد دفعة", "الطالب: ياسين بلحاج — قسم السنة 3", "منذ 5 دقائق", Colors.SUCCESS, Colors.SUCCESS_LIGHT),
            ("👤", "تسجيل طالب جديد", "مريم عبد الرحمان — قسم تحضيري", "منذ 32 دقيقة", Colors.PRIMARY, Colors.PRIMARY_LIGHT),
            ("📋", "أخذ الحضور", "قسم السنة 5 — 28 من 30 حاضر", "منذ ساعة", Colors.INFO, Colors.INFO_LIGHT),
            ("✉️", "إرسال رسائل SMS", "تذكير بالدفع — 37 ولي أمر", "منذ 3 ساعات", Colors.VIOLET, Colors.VIOLET_LIGHT),
            ("⚠️", "تأخر في التسديد", "الطالب: عمر شريف — قسم السنة 2", "أمس، 18:40", Colors.DANGER, Colors.DANGER_LIGHT),
        ]

        for icon, title, meta, time_text, color, bg in activities:
            section.add_widget(ActivityItem(icon, title, meta, time_text, color, bg))

        return section

    # ------------------------------------------------------------------ #
    # Quick actions grid
    # ------------------------------------------------------------------ #
    def _build_quick_actions_section(self) -> SectionCard:
        section = SectionCard(title="إجراءات سريعة")

        grid = QGridLayout()
        grid.setSpacing(10)

        actions = [
            ("👤", "إضافة طالب"),
            ("💳", "تسجيل دفعة"),
            ("📋", "أخذ الحضور"),
            ("✉️", "إرسال SMS"),
            ("📊", "إنشاء تقرير"),
            ("🏫", "إضافة قسم"),
        ]

        for index, (icon, label) in enumerate(actions):
            btn = QuickActionButton(icon, label)
            # Redirect trigger #3: "إضافة طالب" quick-action tile -> Students page
            if label == "إضافة طالب":
                btn.clicked.connect(lambda: self.navigate_requested.emit("students"))
            row, col = divmod(index, 3)
            grid.addWidget(btn, row, col)

        section.add_layout(grid)
        return section