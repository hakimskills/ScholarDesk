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
    BG = "#F4F5FA"              # window / page background
    SURFACE = "#FFFFFF"         # cards, panels
    SURFACE_ALT = "#F7F7FB"     # subtle alternate surface (inputs, rows)
    BORDER = "#E9E9F2"          # hairline borders
    BORDER_STRONG = "#DADAE9"

    # Brand (deep navy — shared across every page/dialog so the app
    # reads as one consistent product instead of a mix of accent colors)
    PRIMARY = "#0F104A"
    PRIMARY_DARK = "#0A0B33"
    PRIMARY_LIGHT = "#E7E7F2"   # soft tint for badges / hovers / selection
    PRIMARY_SOFT = "#4B4C82"    # muted variant for secondary text on brand
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

    # Dashboard menu tiles
    TILE_ACCENT = "#0F104A"
    TILE_ACCENT_HOVER = "#0A0B33"
    TILE_MUTED = "#8890B8"
    TILE_MUTED_HOVER = "#767FAE"

    # Text
    TEXT_PRIMARY = "#181A33"
    TEXT_SECONDARY = "#6B6E8A"
    TEXT_MUTED = "#9C9FB8"
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

    /* ---------- Search box (students list toolbar) ---------- */
    QLineEdit#searchBox {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.PILL}px;
        padding: 10px 18px;
        font-size: 13px;
        min-width: 240px;
        color: {c.TEXT_PRIMARY};
    }}
    QLineEdit#searchBox:focus {{
        border: 1px solid {c.PRIMARY};
        background-color: {c.SURFACE};
    }}
    QLineEdit#searchBox:hover {{
        border: 1px solid {c.BORDER_STRONG};
    }}

    /* ---------- Filter combo boxes ---------- */
    QComboBox#filterCombo {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.PILL}px;
        padding: 9px 16px;
        font-size: 12.5px;
        font-weight: 600;
        color: {c.TEXT_SECONDARY};
        min-width: 130px;
    }}
    QComboBox#filterCombo:hover {{
        border: 1px solid {c.PRIMARY};
        color: {c.PRIMARY};
    }}
    QComboBox#filterCombo:focus {{
        border: 1px solid {c.PRIMARY};
        color: {c.PRIMARY};
    }}
    QComboBox#filterCombo::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox#filterCombo QAbstractItemView {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.MD}px;
        selection-background-color: {c.PRIMARY_LIGHT};
        selection-color: {c.PRIMARY};
        outline: none;
        padding: 4px;
    }}

    QPushButton#primaryButton {{
        background-color: {c.PRIMARY};
        color: {c.TEXT_ON_PRIMARY};
        border: none;
        border-radius: {Radius.PILL}px;
        padding: 10px 22px;
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
    QPushButton#outlineButton {{
        background-color: {c.SURFACE};
        color: {c.TEXT_SECONDARY};
        border: 1px solid {c.BORDER_STRONG};
        border-radius: {Radius.PILL}px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton#outlineButton:hover {{
        background-color: {c.SURFACE_ALT};
        border: 1px solid {c.PRIMARY};
        color: {c.PRIMARY};
    }}
    QPushButton#outlineButton:pressed {{
        padding-top: 11px;
    }}

    /* ---------- Row action buttons (table) ---------- */
    QPushButton#rowActionButton {{
        background-color: transparent;
        border: none;
        border-radius: {Radius.SM}px;
        color: {c.TEXT_SECONDARY};
        font-size: 13px;
        padding: 6px;
        min-width: 28px;
        min-height: 28px;
    }}
    QPushButton#rowActionButton:hover {{
        background-color: {c.PRIMARY_LIGHT};
        color: {c.PRIMARY};
    }}

    /* ---------- Form dialogs (add/edit student, etc.) ---------- */
    QDialog#formDialog {{
        background-color: {c.BG};
    }}
    QLabel#formTitle {{
        font-size: 18px;
        font-weight: 700;
        color: {c.TEXT_PRIMARY};
    }}
    QLabel#formSubtitle {{
        font-size: 12px;
        color: {c.TEXT_SECONDARY};
    }}
    QLabel#formSectionTitle {{
        font-size: 12.5px;
        font-weight: 700;
        color: {c.PRIMARY};
    }}
    QFrame#formHeaderSeparator {{
        background-color: {c.BORDER};
        max-height: 1px;
        min-height: 1px;
        border: none;
    }}
    QFrame#formCard {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.LG}px;
    }}
    QLabel#formFieldLabel {{
        font-size: 11.5px;
        font-weight: 600;
        color: {c.TEXT_SECONDARY};
    }}
    QLineEdit#formInput, QComboBox#formCombo, QDateEdit#formDate {{
        background-color: {c.SURFACE_ALT};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.MD}px;
        padding: 9px 12px;
        font-size: 12.5px;
        color: {c.TEXT_PRIMARY};
        min-height: 18px;
    }}
    QLineEdit#formInput:hover, QComboBox#formCombo:hover, QDateEdit#formDate:hover {{
        border: 1px solid {c.BORDER_STRONG};
    }}
    QLineEdit#formInput:focus, QComboBox#formCombo:focus, QDateEdit#formDate:focus {{
        background-color: {c.SURFACE};
        border: 1px solid {c.PRIMARY};
    }}
    QComboBox#formCombo::drop-down {{
        border: none;
        width: 26px;
    }}
    QComboBox#formCombo QAbstractItemView {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        selection-background-color: {c.PRIMARY_LIGHT};
        selection-color: {c.PRIMARY};
        outline: none;
        padding: 4px;
    }}
    QDateEdit#formDate::drop-down {{
        border: none;
        width: 26px;
    }}

    /* ---------- Table card (students list) ---------- */
    QFrame#tableCard {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.LG}px;
    }}

    QTableWidget#dataTable {{
        background-color: {c.SURFACE};
        border: none;
        gridline-color: transparent;
        selection-background-color: {c.PRIMARY_LIGHT};
    }}
    QTableWidget#dataTable::item {{
        border-bottom: 1px solid {c.BORDER};
        padding: 2px 4px;
    }}
    QTableWidget#dataTable::item:selected {{
        background-color: {c.PRIMARY_LIGHT};
        color: {c.TEXT_PRIMARY};
    }}
    QHeaderView::section {{
        background-color: {c.SURFACE};
        color: {c.TEXT_MUTED};
        border: none;
        border-bottom: 2px solid {c.BORDER};
        padding: 12px 10px;
        font-size: 11.5px;
        font-weight: 700;
    }}

    /* ---------- Header / stat pill ---------- */
    QLabel#pageTitle {{
        font-size: 22px;
        font-weight: 800;
        color: {c.PRIMARY};
    }}
    QLabel#statPill {{
        background-color: {c.PRIMARY_LIGHT};
        color: {c.PRIMARY};
        font-size: 12px;
        font-weight: 700;
        border-radius: {Radius.PILL}px;
        padding: 5px 14px;
    }}
    QFrame#tableCard {{
        border-top: 3px solid {c.PRIMARY};
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

    /* ---------- Dashboard menu tiles ----------
       Rectangular on purpose (no border-radius) — a grid of pill
       buttons reads as a row of CTAs; flat rectangles read as a
       compact toolbar, which fits a denser grid of options better. */
    QFrame#menuTile {{
        border: none;
        border-radius: 0px;
    }}
    QFrame#menuTile[variant="ready"] {{
        background-color: {c.TILE_ACCENT};
    }}
    QFrame#menuTile[variant="ready"]:hover {{
        background-color: {c.TILE_ACCENT_HOVER};
    }}
    QFrame#menuTile[variant="soon"] {{
        background-color: {c.TILE_MUTED};
    }}
    QLabel#menuTileIcon {{
        background-color: transparent;
        font-size: 16px;
    }}
    QLabel#menuTileLabel {{
        background-color: transparent;
        color: {c.PRIMARY_TEXT_ON};
        font-size: 10.5px;
        font-weight: 700;
    }}
    QLabel#menuTileBadge {{
        background-color: rgba(255, 255, 255, 55);
        color: {c.PRIMARY_TEXT_ON};
        font-size: 8.5px;
        font-weight: 700;
        border-radius: 3px;
        padding: 1px 6px;
    }}

    /* ---------- Popups: context menus & message boxes ----------
       QWidget's global "background-color: transparent" rule above
       leaves QMenu/QMessageBox with no real paint surface on some
       platforms, which is what renders as a solid black popup.
       These give both an explicit, themed background instead. */
    QMenu {{
        background-color: {c.SURFACE};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.MD}px;
        padding: 6px;
    }}
    QMenu::item {{
        background-color: transparent;
        color: {c.TEXT_PRIMARY};
        padding: 8px 14px;
        border-radius: {Radius.SM}px;
        font-size: 12.5px;
    }}
    QMenu::item:selected {{
        background-color: {c.PRIMARY_LIGHT};
        color: {c.PRIMARY};
    }}
    QMenu::item:disabled {{
        color: {c.TEXT_MUTED};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {c.BORDER};
        margin: 6px 4px;
    }}

    QMessageBox {{
        background-color: {c.SURFACE};
    }}
    QMessageBox QLabel {{
        color: {c.TEXT_PRIMARY};
        font-size: 12.5px;
        background-color: transparent;
    }}
    QMessageBox QPushButton {{
        background-color: {c.SURFACE_ALT};
        color: {c.TEXT_PRIMARY};
        border: 1px solid {c.BORDER_STRONG};
        border-radius: {Radius.PILL}px;
        padding: 8px 18px;
        font-size: 12.5px;
        font-weight: 600;
        min-width: 72px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {c.PRIMARY_LIGHT};
        border: 1px solid {c.PRIMARY};
        color: {c.PRIMARY};
    }}
    QMessageBox QPushButton:pressed {{
        padding-top: 9px;
    }}

    /* ---------- Checkable student picker (group_students_dialog) ----------
       Same transparent-QWidget issue as the popups above: with no
       explicit styling, QListWidget's built-in checkbox indicator can
       end up nearly invisible against the app's background. Give it
       a clearly-bordered box that's obviously empty when unchecked
       and clearly filled (brand color) when checked. */
    QListWidget#studentPickList {{
        background-color: {c.SURFACE_ALT};
        border: 1px solid {c.BORDER};
        border-radius: {Radius.MD}px;
        padding: 6px;
        font-size: 12.5px;
        color: {c.TEXT_PRIMARY};
    }}
    QListWidget#studentPickList::item {{
        padding: 9px 8px;
        border-radius: {Radius.SM}px;
        margin: 1px 0px;
    }}
    QListWidget#studentPickList::item:hover {{
        background-color: {c.SURFACE};
    }}
    QListWidget#studentPickList::item:selected,
    QListWidget#studentPickList::item:selected:active,
    QListWidget#studentPickList::item:selected:!active {{
        background-color: {c.PRIMARY_LIGHT};
        color: {c.TEXT_PRIMARY};
    }}
    QListWidget#studentPickList::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {c.BORDER_STRONG};
        border-radius: 5px;
        background-color: {c.SURFACE};
    }}
    QListWidget#studentPickList::indicator:hover {{
        border: 2px solid {c.PRIMARY};
    }}
    QListWidget#studentPickList::indicator:checked {{
        border: 2px solid {c.PRIMARY};
        background-color: {c.PRIMARY};
    }}
    """