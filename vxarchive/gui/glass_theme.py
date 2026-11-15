"""
Dark glass, OLED black, and Fluent light stylesheets and theme tokens for VXArchive.
"""
from PyQt6.QtCore import QSettings

DARK_GLASS_STYLE = """
QWidget {
    background-color: #121316;
    color: #e2e8f0;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #121316;
}

/* --- Windows 11 Glass Menu Bar --- */
QMenuBar {
    background-color: transparent;
    color: #cbd5e1;
    padding: 3px 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 12.5px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 5px;
    margin-right: 2px;
}

QMenuBar::item:selected {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: rgba(255, 255, 255, 0.12);
}

/* --- Floating Dark Glass Menus --- */
QMenu {
    background-color: #1b1c20;
    border: 1px solid #2d313a;
    border-radius: 8px;
    padding: 5px;
    color: #e2e8f0;
}

QMenu::item {
    padding: 6px 28px 6px 12px;
    border-radius: 5px;
    font-size: 12.5px;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #64748b;
}

QMenu::separator {
    height: 1px;
    background-color: #2a2e37;
    margin: 4px 8px;
}

/* --- Modern Glass Action Toolbar --- */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(28, 30, 36, 0.95), stop:1 rgba(22, 23, 28, 0.95));
    border-top: none;
    border-left: none;
    border-right: none;
    border-bottom: 1px solid #262932;
    spacing: 4px;
    padding: 5px 8px;
}

QToolBar::separator {
    width: 1px;
    background-color: #2e333d;
    margin: 4px 6px;
}

QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #ffffff;
}

QToolButton:pressed {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

QToolButton:checked {
    background-color: rgba(37, 99, 235, 0.25);
    border: 1px solid #3b82f6;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #252830;
    background-color: #17181c;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #1a1c20;
    color: #94a3b8;
    padding: 7px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #252830;
    margin-right: 2px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #22252c;
    color: #ffffff;
    border-bottom: 2px solid #3b82f6;
}

QTabBar::tab:hover:!selected {
    background-color: #1f2227;
    color: #cbd5e1;
}

/* --- Buttons --- */
QPushButton {
    background-color: #24272f;
    border: 1px solid #353944;
    border-radius: 6px;
    padding: 6px 14px;
    color: #f1f5f9;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #2e323c;
    border-color: #474d5c;
}

QPushButton:pressed {
    background-color: #1b1d22;
}

QPushButton:disabled {
    background-color: #18191d;
    border-color: #252830;
    color: #64748b;
}

/* --- Inputs & Dropdowns --- */
QLineEdit, QComboBox, QSpinBox {
    background-color: #1a1c20;
    border: 1px solid #31353f;
    border-radius: 6px;
    padding: 5px 8px;
    color: #f8fafc;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
    background-color: #1f2127;
}

/* --- Tables & Lists --- */
QTableWidget, QTableView, QTreeView, QListWidget {
    background-color: #16171b;
    border: 1px solid #252830;
    border-radius: 6px;
    gridline-color: #202227;
    selection-background-color: #1d4ed8;
    selection-color: #ffffff;
    alternate-background-color: #191a1e;
}

QTableWidget::item, QTableView::item {
    padding: 4px 6px;
    border-bottom: 1px solid #1c1d22;
}

QHeaderView::section {
    background-color: #1b1d22;
    color: #94a3b8;
    padding: 7px;
    border: none;
    border-right: 1px solid #252830;
    border-bottom: 1px solid #252830;
    font-weight: 600;
    font-size: 11.5px;
    text-transform: uppercase;
}

/* --- Status Bar --- */
QStatusBar {
    background-color: #141518;
    color: #64748b;
    border-top: 1px solid #202227;
    padding: 3px 8px;
    font-size: 11.5px;
}

/* --- ScrollBars --- */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2e323b;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #424754;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

OLED_BLACK_STYLE = """
QWidget {
    background-color: #000000;
    color: #f1f5f9;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #000000;
}

QMenuBar {
    background-color: #000000;
    color: #94a3b8;
    padding: 3px 6px;
    border-bottom: 1px solid #1a1a1a;
    font-size: 12.5px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 5px;
}

QMenuBar::item:selected {
    background-color: #18181b;
    color: #ffffff;
}

QMenu {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 5px;
    color: #f4f4f5;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QToolBar {
    background: #000000;
    border-bottom: 1px solid #18181b;
    spacing: 4px;
    padding: 5px 8px;
}

QToolButton {
    background: transparent;
    border-radius: 6px;
    padding: 5px 10px;
    color: #e4e4e7;
}

QToolButton:hover {
    background-color: #18181b;
    color: #ffffff;
}

QToolButton:checked {
    background-color: #1e3a8a;
    border: 1px solid #3b82f6;
}

QTabWidget::pane {
    border: 1px solid #18181b;
    background-color: #000000;
}

QTabBar::tab {
    background-color: #09090b;
    color: #71717a;
    padding: 7px 16px;
    border: 1px solid #18181b;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #141416;
    color: #ffffff;
    border-bottom: 2px solid #38bdf8;
}

QPushButton {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 6px 14px;
    color: #ffffff;
}

QPushButton:hover {
    background-color: #18181b;
    border-color: #3f3f46;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #09090b;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 5px 8px;
    color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #38bdf8;
}

QTableWidget, QTableView, QListWidget {
    background-color: #000000;
    border: 1px solid #18181b;
    selection-background-color: #1e40af;
    selection-color: #ffffff;
    alternate-background-color: #050505;
}

QHeaderView::section {
    background-color: #09090b;
    color: #71717a;
    padding: 7px;
    border: none;
    border-bottom: 1px solid #18181b;
}

QStatusBar {
    background-color: #000000;
    color: #52525b;
    border-top: 1px solid #18181b;
}
"""

LIGHT_GLASS_STYLE = """
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #f8fafc;
}

QMenuBar {
    background-color: #ffffff;
    color: #334155;
    padding: 3px 6px;
    border-bottom: 1px solid #e2e8f0;
    font-size: 12.5px;
}

QMenuBar::item:selected {
    background-color: #f1f5f9;
    color: #0f172a;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 5px;
    color: #1e293b;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 4px;
    padding: 5px 8px;
}

QToolButton {
    background: transparent;
    border-radius: 6px;
    padding: 5px 10px;
    color: #334155;
}

QToolButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QToolButton:checked {
    background-color: #dbeafe;
    border: 1px solid #3b82f6;
    color: #1d4ed8;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f1f5f9;
    color: #64748b;
    padding: 7px 16px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0f172a;
    border-bottom: 2px solid #2563eb;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 14px;
    color: #0f172a;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 5px 8px;
    color: #0f172a;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #2563eb;
}

QTableWidget, QTableView, QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    alternate-background-color: #f8fafc;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #64748b;
    padding: 7px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
}

QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
}
"""


class ThemeManager:
    """Manages application themes and persistence."""
    THEMES = {
        "dark": ("Dark Glass (Fluent Mica)", DARK_GLASS_STYLE),
        "oled": ("OLED Pure Black", OLED_BLACK_STYLE),
        "light": ("Fluent Light Glass", LIGHT_GLASS_STYLE)
    }

    @classmethod
    def apply_theme(cls, app_or_widget, theme_name: str = "dark"):
        if theme_name not in cls.THEMES:
            theme_name = "dark"
        style = cls.THEMES[theme_name][1]
        app_or_widget.setStyleSheet(style)
        try:
            settings = QSettings("VXArchive", "VXArchive")
            settings.setValue("theme", theme_name)
        except Exception:
            pass

    @classmethod
    def get_current_theme(cls) -> str:
        try:
            settings = QSettings("VXArchive", "VXArchive")
            t = settings.value("theme", "dark")
            return t if t in cls.THEMES else "dark"
        except Exception:
            return "dark"


def apply_dark_glass_theme(app_or_widget):
    ThemeManager.apply_theme(app_or_widget, ThemeManager.get_current_theme())
