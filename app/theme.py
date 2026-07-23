# -*- coding: utf-8 -*-
"""
app/theme.py

Central design system for the School Manager application.
Holds the color palette, spacing scale, font configuration and the
global QSS stylesheet. Keeping all of this in one place makes it easy
to re-skin the app later (e.g. add a dark theme) without touching any
widget code.
"""

import os
from PySide6.QtGui import QFontDatabase, QFont


class Colors:
    """Application color palette."""

    # Surfaces
    BG = "#F3F5FB"              # window / page background
    SURFACE = "#FFFFFF"         # cards, panels
    SURFACE_ALT = "#F8F9FD"     # subtle alternate surface (inputs, rows)
    BORDER = "#E8EAF3"          # hairline borders
    BORDER_STRONG = "#DBDEEC"

    # Brand
    PRIMARY = "#4F5FF0"
    PRIMARY_DARK = "#3C48C9"
    PRIMARY_LIGHT = "#EEF0FE"
    PRIMARY_TEXT_ON = "#FFFFFF"

    # Status
    SUCCESS = "#1FB579"
    SUCCESS_LIGHT = "#E3F9EF"
    DANGER = "#F1506E"
    DANGER_LIGHT = "#FDEAEF"
    WARNING = "#F5A524"
    WARNING_LIGHT = "#FDF2E1"
    INFO = "#2FB0E8"
    INFO_LIGHT = "#E7F7FD"
    VIOLET = "#9B6BF2"
    VIOLET_LIGHT = "#F1EAFE"

    # Text
    TEXT_PRIMARY = "#1B2140"
    TEXT_SECONDARY = "#6B7189"
    TEXT_MUTED = "#9CA0B8"
    TEXT_ON_PRIMARY = "#FFFFFF"


class Spacing:
    XS = 6
    SM = 10
    MD = 16
    LG = 20
    XL = 28


class Radius:
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    PILL = 999


# Preferred Arabic-friendly font stack. If a bundled TTF exists under
# assets/fonts it is loaded and placed first; otherwise we gracefully
# fall back to fonts that ship with Windows and render Arabic well.
FONT_FAMILY_FALLBACKS = ["Cairo", "Tajawal", "Segoe UI", "Tahoma", "Arial"]


def load_app_fonts(assets_dir: str) -> str:
    """
    Loads any .ttf/.otf fonts bundled in assets/fonts and returns the
    best available Arabic-friendly font family name to use as the
    application's default font.
    """
    fonts_dir = os.path.join(assets_dir, "fonts")
    loaded_families = []

    if os.path.isdir(fonts_dir):
        for file_name in os.listdir(fonts_dir):
            if file_name.lower().endswith((".ttf", ".otf")):
                font_id = QFontDatabase.addApplicationFont(
                    os.path.join(fonts_dir, file_name)
                )
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    loaded_families.extend(families)

    for family in loaded_families + FONT_FAMILY_FALLBACKS:
        if family in QFontDatabase.families():
            return family

    # As a last resort, just return the first fallback name. Qt will
    # substitute a suitable system font automatically.
    return FONT_FAMILY_FALLBACKS[0]


def build_app_font(family: str, point_size: int = 10) -> QFont:
    font = QFont(family, point_size)
    font.setStyleStrategy(QFont.PreferAntialias)
    return font


def build_stylesheet(font_family: str) -> str:
    """Returns the global QSS used across the dashboard."""
    c = Colors
    return f"""
    * {{
        font-family: "{font_family}";
        outline: none;
    }}

    QWidget {{
        background-color: transparent;
        color: {c.TEXT_PRIMARY};
    }}

    QWidget#pageRoot, QWidget#scrollContent {{
        background-color: {c.BG};
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 0px 4px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {c.BORDER_STRONG};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c.TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        height: 0px;
    }}

    /* ---------- Top bar ---------- */
    QLabel#greetingTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {c.TEXT_PRIMARY};
    }}
    QLabel#greetingSubtitle {{
        font-size: 13px;
        color: {c.TEXT_SECONDARY};
    }}
    QLabel#dateLabel {{
        font-size: 12px;
        color: {c.TEXT_SECONDARY};
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.PILL}px;
        padding: 8px 16px;
    }}
    QLineEdit#searchBox {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.PILL}px;
        padding: 9px 16px;
        font-size: 13px;
        min-width: 220px;
        color: {c.TEXT_PRIMARY};
    }}
    QLineEdit#searchBox:focus {{
        border: 1px solid {c.PRIMARY};
    }}
    QPushButton#iconButton {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.PILL}px;
        min-width: 38px;
        max-width: 38px;
        min-height: 38px;
        max-height: 38px;
        font-size: 15px;
    }}
    QPushButton#iconButton:hover {{
        background-color: {c.PRIMARY_LIGHT};
        border: 1px solid {c.PRIMARY};
    }}
    QPushButton#primaryButton {{
        background-color: {c.PRIMARY};
        color: {c.TEXT_ON_PRIMARY};
        border: none;
        border-radius: {Radius.PILL}px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {c.PRIMARY_DARK};
    }}
    QPushButton#primaryButton:pressed {{
        background-color: {c.PRIMARY_DARK};
        padding-top: 11px;
    }}

    /* ---------- Cards ---------- */
    QFrame#statCard {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.LG}px;
    }}
    QFrame#statCard:hover {{
        border: 1px solid {c.PRIMARY_LIGHT};
    }}
    QLabel#statIcon {{
        border-radius: {Radius.MD}px;
        font-size: 19px;
        qproperty-alignment: AlignCenter;
    }}
    QLabel#statValue {{
        font-size: 25px;
        font-weight: 800;
        color: {c.TEXT_PRIMARY};
    }}
    QLabel#statTitle {{
        font-size: 12.5px;
        color: {c.TEXT_SECONDARY};
        font-weight: 500;
    }}
    QLabel#trendUp {{
        color: {c.SUCCESS};
        font-size: 11.5px;
        font-weight: 700;
        background-color: {c.SUCCESS_LIGHT};
        border-radius: {Radius.SM}px;
        padding: 2px 8px;
    }}
    QLabel#trendDown {{
        color: {c.DANGER};
        font-size: 11.5px;
        font-weight: 700;
        background-color: {c.DANGER_LIGHT};
        border-radius: {Radius.SM}px;
        padding: 2px 8px;
    }}
    QLabel#trendCaption {{
        color: {c.TEXT_MUTED};
        font-size: 11px;
    }}

    /* ---------- Section card ---------- */
    QFrame#sectionCard {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.LG}px;
    }}
    QLabel#sectionTitle {{
        font-size: 15px;
        font-weight: 700;
        color: {c.TEXT_PRIMARY};
    }}
    QLabel#sectionSubtitle {{
        font-size: 11.5px;
        color: {c.TEXT_MUTED};
    }}
    QFrame#sectionSeparator {{
        background-color: {c.BORDER};
        max-height: 1px;
        min-height: 1px;
        border: none;
    }}
    QPushButton#chipButton {{
        background-color: {c.SURFACE_ALT};
        border: 1px solid {c.BORDER};
        color: {c.TEXT_SECONDARY};
        border-radius: {Radius.PILL}px;
        padding: 5px 14px;
        font-size: 11.5px;
        font-weight: 600;
    }}
    QPushButton#chipButton:checked {{
        background-color: {c.PRIMARY};
        color: {c.TEXT_ON_PRIMARY};
        border: 1px solid {c.PRIMARY};
    }}
    QPushButton#linkButton {{
        background-color: transparent;
        border: none;
        color: {c.PRIMARY};
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#linkButton:hover {{
        color: {c.PRIMARY_DARK};
        text-decoration: underline;
    }}

    /* ---------- Activity list ---------- */
    QFrame#activityItem {{
        background-color: transparent;
        border-radius: {Radius.MD}px;
    }}
    QFrame#activityItem:hover {{
        background-color: {c.SURFACE_ALT};
    }}
    QLabel#activityIcon {{
        border-radius: {Radius.MD}px;
        font-size: 15px;
        qproperty-alignment: AlignCenter;
    }}
    QLabel#activityTitle {{
        font-size: 12.5px;
        font-weight: 600;
        color: {c.TEXT_PRIMARY};
    }}
    QLabel#activityMeta {{
        font-size: 11px;
        color: {c.TEXT_MUTED};
    }}
    QLabel#activityTime {{
        font-size: 11px;
        color: {c.TEXT_MUTED};
    }}

    /* ---------- Payment status rows ---------- */
    QLabel#rowLabel {{
        font-size: 12.5px;
        font-weight: 600;
        color: {c.TEXT_PRIMARY};
    }}
    QLabel#rowValue {{
        font-size: 12.5px;
        font-weight: 700;
        color: {c.TEXT_SECONDARY};
    }}
    QProgressBar#statusBar {{
        border: none;
        border-radius: 5px;
        background-color: {c.SURFACE_ALT};
        min-height: 10px;
        max-height: 10px;
    }}
    QProgressBar#statusBar::chunk {{
        border-radius: 5px;
    }}

    /* ---------- Quick actions ---------- */
    QPushButton#quickAction {{
        background-color: {c.SURFACE_ALT};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.MD}px;
        color: {c.TEXT_PRIMARY};
        font-size: 12px;
        font-weight: 600;
        padding: 14px 6px;
    }}
    QPushButton#quickAction:hover {{
        background-color: {c.PRIMARY_LIGHT};
        border: 1px solid {c.PRIMARY};
        color: {c.PRIMARY_DARK};
    }}
    """