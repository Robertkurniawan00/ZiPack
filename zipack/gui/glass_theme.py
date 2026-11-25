"""
Token-driven Dark Glass, OLED Pure Black, and Fluent Light stylesheets and theme manager for ZiPack.
"""
from PyQt6.QtCore import QSettings

_THEME_TOKENS = {
    "dark": {
        "bg_base": "#111318",
        "bg_surface": "#161920",
        "bg_elevated": "#1d212a",
        "bg_input": "#181b22",
        "bg_hover": "rgba(255, 255, 255, 0.07)",
        "bg_pressed": "rgba(255, 255, 255, 0.04)",
        "bg_alt_row": "#181b23",
        "menu_bg": "#1a1d24",
        "toolbar_bg_top": "rgba(26, 29, 36, 0.96)",
        "toolbar_bg_bot": "rgba(20, 22, 28, 0.96)",
        "header_bg": "#1a1d24",
        "status_bg": "#12141a",
        "border_subtle": "#262a35",
        "border_strong": "#353b4a",
        "border_focus": "#3b82f6",
        "text_primary": "#f1f5f9",
        "text_secondary": "#cbd5e1",
        "text_muted": "#64748b",
        "accent": "#2563eb",
        "accent_hover": "#3b82f6",
        "accent_pressed": "#1d4ed8",
        "accent_soft": "rgba(37, 99, 235, 0.22)",
        "scroll_handle": "#2e3440",
        "scroll_hover": "#434c5e",
        "selection_bg": "#1d4ed8",
        "selection_fg": "#ffffff",
        "tooltip_bg": "#1e222b",
    },
    "oled": {
        "bg_base": "#000000",
        "bg_surface": "#050507",
        "bg_elevated": "#0e0f13",
        "bg_input": "#090a0d",
        "bg_hover": "rgba(255, 255, 255, 0.08)",
        "bg_pressed": "rgba(255, 255, 255, 0.04)",
        "bg_alt_row": "#08090c",
        "menu_bg": "#090a0d",
        "toolbar_bg_top": "#07080a",
        "toolbar_bg_bot": "#020203",
        "header_bg": "#0a0b0e",
        "status_bg": "#000000",
        "border_subtle": "#1c1e24",
        "border_strong": "#2c303a",
        "border_focus": "#3b82f6",
        "text_primary": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#64748b",
        "accent": "#2563eb",
        "accent_hover": "#3b82f6",
        "accent_pressed": "#1d4ed8",
        "accent_soft": "rgba(37, 99, 235, 0.28)",
        "scroll_handle": "#27272a",
        "scroll_hover": "#3f3f46",
        "selection_bg": "#2563eb",
        "selection_fg": "#ffffff",
        "tooltip_bg": "#111216",
    },
    "light": {
        "bg_base": "#f3f5f9",
        "bg_surface": "#ffffff",
        "bg_elevated": "#f8fafc",
        "bg_input": "#ffffff",
        "bg_hover": "rgba(15, 23, 42, 0.05)",
        "bg_pressed": "rgba(15, 23, 42, 0.09)",
        "bg_alt_row": "#f8fafc",
        "menu_bg": "#ffffff",
        "toolbar_bg_top": "#ffffff",
        "toolbar_bg_bot": "#f8fafc",
        "header_bg": "#f1f5f9",
        "status_bg": "#ffffff",
        "border_subtle": "#e2e8f0",
        "border_strong": "#cbd5e1",
        "border_focus": "#2563eb",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "accent_pressed": "#1e40af",
        "accent_soft": "rgba(37, 99, 235, 0.12)",
        "scroll_handle": "#cbd5e1",
        "scroll_hover": "#94a3b8",
        "selection_bg": "#2563eb",
        "selection_fg": "#ffffff",
        "tooltip_bg": "#ffffff",
    },
}


def build_stylesheet(tokens: dict) -> str:
    """Generates a complete, cohesive Fluent Glass stylesheet from semantic color tokens."""
    t = tokens
    return f"""
QWidget {{
    background-color: {t["bg_base"]};
    color: {t["text_primary"]};
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {t["bg_base"]};
}}

QLabel {{
    background-color: transparent;
}}

/* --- Menu Bar --- */
QMenuBar {{
    background-color: transparent;
    color: {t["text_secondary"]};
    padding: 3px 8px;
    border-bottom: 1px solid {t["border_subtle"]};
    font-size: 12.5px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
    border-radius: 5px;
    margin-right: 2px;
}}

QMenuBar::item:selected {{
    background-color: {t["bg_hover"]};
    color: {t["text_primary"]};
}}

QMenuBar::item:pressed {{
    background-color: {t["bg_pressed"]};
}}

/* --- Floating Menus --- */
QMenu {{
    background-color: {t["menu_bg"]};
    border: 1px solid {t["border_strong"]};
    border-radius: 8px;
    padding: 6px;
    color: {t["text_primary"]};
}}

QMenu::item {{
    background-color: transparent;
    min-width: 195px;
    padding: 6px 28px 6px 24px;
    border-radius: 5px;
    font-size: 12.5px;
    margin: 1px 4px;
}}

QMenu::item:selected {{
    background-color: {t["accent"]};
    color: #ffffff;
}}

QMenu::item:disabled {{
    color: {t["text_muted"]};
}}

QMenu::separator {{
    height: 1px;
    background-color: {t["border_subtle"]};
    margin: 4px 8px;
}}

/* --- Action Toolbar --- */
QToolBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {t["toolbar_bg_top"]}, stop:1 {t["toolbar_bg_bot"]});
    border: none;
    border-bottom: 1px solid {t["border_subtle"]};
    spacing: 4px;
    padding: 5px 10px;
}}

QToolBar::separator {{
    width: 1px;
    background-color: {t["border_subtle"]};
    margin: 4px 6px;
}}

QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 9px;
    color: {t["text_secondary"]};
    font-size: 12px;
    font-weight: 500;
}}

QToolButton:hover {{
    background-color: {t["bg_hover"]};
    border: 1px solid {t["border_subtle"]};
    color: {t["text_primary"]};
}}

QToolButton:pressed {{
    background-color: {t["bg_pressed"]};
}}

QToolButton:disabled {{
    color: {t["text_muted"]};
}}

QToolButton:checked {{
    background-color: {t["accent_soft"]};
    border: 1px solid {t["border_focus"]};
    color: {t["text_primary"]};
}}

/* --- Tabs --- */
QTabWidget::pane {{
    border: 1px solid {t["border_subtle"]};
    background-color: {t["bg_surface"]};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {t["bg_elevated"]};
    color: {t["text_muted"]};
    padding: 7px 14px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    border: 1px solid {t["border_subtle"]};
    border-bottom: none;
    margin-right: 3px;
    font-size: 12px;
    font-weight: 500;
    min-width: 90px;
}}

QTabBar::tab:selected {{
    background-color: {t["bg_surface"]};
    color: {t["text_primary"]};
    border-bottom: 2px solid {t["border_focus"]};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: {t["bg_hover"]};
    color: {t["text_secondary"]};
}}

/* --- Buttons --- */
QPushButton {{
    background-color: {t["bg_elevated"]};
    border: 1px solid {t["border_strong"]};
    border-radius: 6px;
    padding: 6px 14px;
    color: {t["text_primary"]};
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {t["bg_hover"]};
    border-color: {t["border_focus"]};
}}

QPushButton:pressed {{
    background-color: {t["bg_pressed"]};
}}

QPushButton:disabled {{
    background-color: {t["bg_base"]};
    border-color: {t["border_subtle"]};
    color: {t["text_muted"]};
}}

QPushButton[variant="primary"] {{
    background-color: {t["accent"]};
    border: 1px solid {t["accent"]};
    color: #ffffff;
    font-weight: 600;
}}

QPushButton[variant="primary"]:hover {{
    background-color: {t["accent_hover"]};
    border-color: {t["accent_hover"]};
}}

QPushButton[variant="primary"]:pressed {{
    background-color: {t["accent_pressed"]};
}}

QPushButton[variant="danger"] {{
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
    font-weight: 600;
}}

QPushButton[variant="danger"]:hover {{
    background-color: #ef4444;
}}

/* --- Inputs & Dropdowns --- */
QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit {{
    background-color: {t["bg_input"]};
    border: 1px solid {t["border_strong"]};
    border-radius: 6px;
    padding: 5px 9px;
    color: {t["text_primary"]};
    selection-background-color: {t["selection_bg"]};
    selection-color: {t["selection_fg"]};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {t["border_focus"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}

QComboBox QAbstractItemView {{
    background-color: {t["menu_bg"]};
    border: 1px solid {t["border_strong"]};
    selection-background-color: {t["accent"]};
    selection-color: #ffffff;
}}

/* --- Group Boxes & Checkboxes --- */
QGroupBox {{
    background-color: {t["bg_surface"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: {t["text_secondary"]};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {t["text_secondary"]};
}}

QCheckBox, QRadioButton {{
    background-color: transparent;
    spacing: 8px;
    color: {t["text_primary"]};
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {t["border_strong"]};
    background-color: {t["bg_input"]};
}}

QCheckBox::indicator {{
    border-radius: 4px;
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {t["accent"]};
    border-color: {t["accent"]};
}}

/* --- Progress Bar --- */
QProgressBar {{
    background-color: {t["bg_elevated"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 6px;
    text-align: center;
    color: {t["text_primary"]};
    font-size: 11px;
    font-weight: 600;
    min-height: 18px;
}}

QProgressBar::chunk {{
    background-color: {t["accent"]};
    border-radius: 5px;
}}

/* --- Tables & Lists --- */
QTableWidget, QTableView, QTreeView, QListWidget {{
    background-color: {t["bg_surface"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 8px;
    gridline-color: {t["border_subtle"]};
    selection-background-color: {t["selection_bg"]};
    selection-color: {t["selection_fg"]};
    alternate-background-color: {t["bg_alt_row"]};
    outline: none;
}}

QTableWidget::item, QTableView::item, QListWidget::item {{
    padding: 5px 8px;
    border-bottom: 1px solid {t["border_subtle"]};
}}

QTableWidget::item:hover, QTableView::item:hover, QListWidget::item:hover {{
    background-color: {t["bg_hover"]};
}}

QHeaderView::section {{
    background-color: {t["header_bg"]};
    color: {t["text_muted"]};
    padding: 7px 8px;
    border: none;
    border-right: 1px solid {t["border_subtle"]};
    border-bottom: 1px solid {t["border_subtle"]};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}}

/* --- Status Bar --- */
QStatusBar {{
    background-color: {t["status_bg"]};
    color: {t["text_muted"]};
    border-top: 1px solid {t["border_subtle"]};
    padding: 3px 10px;
    font-size: 11.5px;
}}

QStatusBar::item {{
    border: none;
}}

QLabel#statusBadge {{
    background-color: {t["bg_elevated"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 4px;
    padding: 2px 8px;
    color: {t["text_secondary"]};
    font-size: 11px;
    font-weight: 500;
}}

/* --- ScrollBars --- */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 2px;
}}

QScrollBar:horizontal {{
    border: none;
    background: transparent;
    height: 8px;
    margin: 2px;
}}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {t["scroll_handle"]};
    min-height: 24px;
    min-width: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
    background: {t["scroll_hover"]};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
    width: 0px;
}}

/* --- ToolTips --- */
QToolTip {{
    background-color: {t["tooltip_bg"]};
    color: {t["text_primary"]};
    border: 1px solid {t["border_strong"]};
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 12px;
}}

/* --- Breadcrumb Address Bar --- */
#breadcrumbAddressBar {{
    background-color: {t["bg_surface"]};
    border: 1px solid {t["border_subtle"]};
    border-radius: 7px;
    max-height: 36px;
}}

#breadcrumbAddressBar QPushButton.crumb-btn {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 3px 8px;
    color: {t["text_secondary"]};
    font-size: 12px;
    font-weight: 500;
}}

#breadcrumbAddressBar QPushButton.crumb-btn:hover {{
    background-color: {t["bg_hover"]};
    border: 1px solid {t["border_subtle"]};
    color: {t["text_primary"]};
}}

#breadcrumbAddressBar QLabel.crumb-sep {{
    color: {t["text_muted"]};
    font-size: 12px;
    padding: 0 2px;
    background: transparent;
}}

#breadcrumbAddressBar QLineEdit {{
    background-color: {t["bg_input"]};
    border: 1px solid {t["border_focus"]};
    border-radius: 5px;
    padding: 2px 8px;
    color: {t["text_primary"]};
    font-size: 12px;
}}

#breadcrumbAddressBar QPushButton#btnToggleEdit {{
    background: transparent;
    border: none;
    border-radius: 5px;
    padding: 2px;
}}

#breadcrumbAddressBar QPushButton#btnToggleEdit:hover {{
    background-color: {t["bg_hover"]};
}}

/* --- New Tab Corner Button --- */
QPushButton#btnNewTabCorner {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 15px;
    font-weight: 600;
    color: {t["text_secondary"]};
    margin: 2px 4px;
}}

QPushButton#btnNewTabCorner:hover {{
    background-color: {t["bg_hover"]};
    border: 1px solid {t["border_subtle"]};
    color: {t["text_primary"]};
}}
"""


DARK_GLASS_STYLE = build_stylesheet(_THEME_TOKENS["dark"])
OLED_BLACK_STYLE = build_stylesheet(_THEME_TOKENS["oled"])
LIGHT_GLASS_STYLE = build_stylesheet(_THEME_TOKENS["light"])


class ThemeManager:
    """Manages application themes and persistence."""
    THEMES = {
        "dark": ("Dark Glass (Fluent Mica)", DARK_GLASS_STYLE),
        "oled": ("OLED Pure Black", OLED_BLACK_STYLE),
        "light": ("Fluent Light Glass", LIGHT_GLASS_STYLE),
    }

    @classmethod
    def apply_theme(cls, app_or_widget, theme_name: str = "dark"):
        if theme_name not in cls.THEMES:
            theme_name = "dark"
        style = cls.THEMES[theme_name][1]
        app_or_widget.setStyleSheet(style)
        try:
            settings = QSettings("ZiPack", "ZiPack")
            settings.setValue("theme", theme_name)
        except Exception:
            pass

    @classmethod
    def get_current_theme(cls) -> str:
        try:
            settings = QSettings("ZiPack", "ZiPack")
            t = settings.value("theme", None)
            return t if t in cls.THEMES else "dark"
        except Exception:
            return "dark"


def apply_dark_glass_theme(app_or_widget):
    ThemeManager.apply_theme(app_or_widget, ThemeManager.get_current_theme())
