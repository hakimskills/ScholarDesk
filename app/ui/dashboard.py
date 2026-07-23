# -*- coding: utf-8 -*-
"""
app/ui/dashboard.py

The main Dashboard page for the School Manager application.
Pure UI: all data below is realistic placeholder/sample data. Wire it
up to app/services + app/models once the SQLite layer is ready —
every section exposes simple methods (see the TODOs) for refreshing
with real data without touching the layout.
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
    QSizePolicy,
    QSpacerItem,
)
from PySide6.QtCore import Qt

from app.theme import Colors
from app.widgets import (
    StatCard,
    SectionCard,
    ActivityItem,
    QuickActionButton,
    BarChartWidget,
    DonutChartWidget,
    StatusRow,
)


class Dashboard(QWidget):
    """The dashboard / home page shown after login."""

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
        content_layout.addLayout(self._build_stats_row())
        content_layout.addLayout(self._build_main_grid())

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)

    # ------------------------------------------------------------------ #
    # Top bar: greeting + search + quick actions
    # ------------------------------------------------------------------ #
    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(16)

        # Greeting (right side in RTL)
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

        # Date pill
        date_label = QLabel("الخميس، 23 يوليو 2026")
        date_label.setObjectName("dateLabel")
        bar.addWidget(date_label)

        # Search box
        search_box = QLineEdit()
        search_box.setObjectName("searchBox")
        search_box.setPlaceholderText("🔍  بحث عن طالب، قسم أو دفعة...")
        search_box.setAlignment(Qt.AlignRight)
        search_box.setFixedWidth(240)
        bar.addWidget(search_box)

        # Notification bell
        bell_btn = QPushButton("🔔")
        bell_btn.setObjectName("iconButton")
        bell_btn.setCursor(Qt.PointingHandCursor)
        bar.addWidget(bell_btn)

        # Add student (primary CTA)
        add_student_btn = QPushButton("+  إضافة طالب جديد")
        add_student_btn.setObjectName("primaryButton")
        add_student_btn.setCursor(Qt.PointingHandCursor)
        bar.addWidget(add_student_btn)

        return bar

    # ------------------------------------------------------------------ #
    # KPI stat cards row
    # ------------------------------------------------------------------ #
    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)

        students_card = StatCard(
            icon="🎓",
            title="عدد الطلاب المسجلين",
            value="512",
            trend_text="4.2%",
            trend_positive=True,
            accent_color=Colors.PRIMARY,
            accent_bg=Colors.PRIMARY_LIGHT,
        )
        classes_card = StatCard(
            icon="📚",
            title="عدد الأقسام النشطة",
            value="24",
            trend_text="2 أقسام جديدة",
            trend_positive=True,
            accent_color=Colors.VIOLET,
            accent_bg=Colors.VIOLET_LIGHT,
        )
        revenue_card = StatCard(
            icon="💰",
            title="مداخيل هذا الشهر",
            value="486,000 دج",
            trend_text="8.6%",
            trend_positive=True,
            accent_color=Colors.SUCCESS,
            accent_bg=Colors.SUCCESS_LIGHT,
        )
        unpaid_card = StatCard(
            icon="⚠️",
            title="طلاب غير مسددين",
            value="37",
            trend_text="12%",
            trend_positive=False,
            accent_color=Colors.DANGER,
            accent_bg=Colors.DANGER_LIGHT,
        )

        for card in (students_card, classes_card, revenue_card, unpaid_card):
            row.addWidget(card, 1)

        return row

    # ------------------------------------------------------------------ #
    # Main content grid: charts / lists / quick actions
    # ------------------------------------------------------------------ #
    def _build_main_grid(self) -> QHBoxLayout:
        grid = QHBoxLayout()
        grid.setSpacing(18)

        main_col = QVBoxLayout()
        main_col.setSpacing(18)
        main_col.addWidget(self._build_revenue_section())
        main_col.addWidget(self._build_payment_status_section())

        side_col = QVBoxLayout()
        side_col.setSpacing(18)
        side_col.addWidget(self._build_attendance_section())
        side_col.addWidget(self._build_activities_section())
        side_col.addWidget(self._build_quick_actions_section())

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
    # Revenue chart section
    # ------------------------------------------------------------------ #
    def _build_revenue_section(self) -> SectionCard:
        chips = QHBoxLayout()
        chips.setSpacing(8)
        monthly_chip = QPushButton("شهري")
        monthly_chip.setObjectName("chipButton")
        monthly_chip.setCheckable(True)
        monthly_chip.setChecked(True)
        monthly_chip.setCursor(Qt.PointingHandCursor)

        weekly_chip = QPushButton("أسبوعي")
        weekly_chip.setObjectName("chipButton")
        weekly_chip.setCheckable(True)
        weekly_chip.setCursor(Qt.PointingHandCursor)

        chips.addWidget(weekly_chip)
        chips.addWidget(monthly_chip)
        chips_widget = QWidget()
        chips_widget.setLayout(chips)

        section = SectionCard(
            title="نظرة عامة على الإيرادات",
            subtitle="مقارنة المداخيل الشهرية لآخر 6 أشهر",
            trailing=chips_widget,
        )

        revenue_data = [
            ("فيفري", 320),
            ("مارس", 355),
            ("أفريل", 298),
            ("ماي", 410),
            ("جوان", 402),
            ("جويلية", 486),
        ]
        chart = BarChartWidget(revenue_data, bar_color=Colors.PRIMARY)
        chart.setMinimumHeight(190)
        section.add_widget(chart)

        # Summary strip under the chart
        summary_row = QHBoxLayout()
        summary_row.setSpacing(24)
        for label, value, color in [
            ("إجمالي السنة الحالية", "2,271,000 دج", Colors.TEXT_PRIMARY),
            ("متوسط شهري", "378,500 دج", Colors.TEXT_PRIMARY),
            ("نمو مقارنة بالسنة الماضية", "+ 14.3%", Colors.SUCCESS),
        ]:
            box = QVBoxLayout()
            box.setSpacing(2)
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {color};")
            v.setAlignment(Qt.AlignRight)
            t = QLabel(label)
            t.setObjectName("sectionSubtitle")
            t.setAlignment(Qt.AlignRight)
            box.addWidget(v)
            box.addWidget(t)
            summary_row.addLayout(box)
        summary_row.addStretch(1)
        section.add_layout(summary_row)

        return section

    # ------------------------------------------------------------------ #
    # Payment status breakdown section
    # ------------------------------------------------------------------ #
    def _build_payment_status_section(self) -> SectionCard:
        section = SectionCard(
            title="حالة تسديد الرسوم",
            subtitle="لشهر جويلية 2026 — إجمالي 512 طالب",
        )

        section.add_widget(StatusRow(Colors.SUCCESS, "مسدد بالكامل", "438 طالب", 86))
        section.add_widget(StatusRow(Colors.WARNING, "مسدد جزئياً", "37 طالب", 7))
        section.add_widget(StatusRow(Colors.DANGER, "غير مسدد", "37 طالب", 7))

        return section

    # ------------------------------------------------------------------ #
    # Attendance donut section
    # ------------------------------------------------------------------ #
    def _build_attendance_section(self) -> SectionCard:
        section = SectionCard(
            title="نسبة الحضور اليوم",
            subtitle="جميع الأقسام — الخميس 23 جويلية",
        )

        donut = DonutChartWidget(
            segments=[
                ("حاضر", 452, Colors.SUCCESS),
                ("متأخر", 24, Colors.WARNING),
                ("غائب", 36, Colors.DANGER),
            ],
            center_value="88%",
            center_label="نسبة الحضور",
        )
        donut.setFixedHeight(190)
        section.add_widget(donut)

        legend = QGridLayout()
        legend.setHorizontalSpacing(16)
        legend.setVerticalSpacing(6)
        legend_items = [
            (Colors.SUCCESS, "حاضر", "452"),
            (Colors.WARNING, "متأخر", "24"),
            (Colors.DANGER, "غائب", "36"),
        ]
        for i, (color, label, count) in enumerate(legend_items):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 11px;")
            text = QLabel(f"{label}  ·  {count}")
            text.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY};")
            row_box = QHBoxLayout()
            row_box.setSpacing(6)
            row_box.addWidget(dot)
            row_box.addWidget(text)
            row_box.addStretch(1)
            wrapper = QWidget()
            wrapper.setLayout(row_box)
            legend.addWidget(wrapper, 0, i)
        section.add_layout(legend)

        return section

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
            row, col = divmod(index, 3)
            grid.addWidget(btn, row, col)

        section.add_layout(grid)
        return section