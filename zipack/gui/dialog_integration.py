"""
Windows Explorer shell integration configuration dialog.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QCheckBox, QLabel, QPushButton, QGridLayout, QMessageBox
)
from ..core.shell_integration import ShellIntegration


class SystemIntegrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Shell Integration")
        self.resize(520, 440)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        status = ShellIntegration.get_status()
        status_txt = "Active (Registered in HKCU)" if status.get("context_menu") else "Not Registered"
        self.lbl_status = QLabel(f"Current Shell Status: <b>{status_txt}</b>")
        main_layout.addWidget(self.lbl_status)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)

        # Tab 1: Context Menu
        tab1 = QWidget()
        t1_layout = QVBoxLayout(tab1)
        self.chk_cascaded = QCheckBox("Cascaded Submenu (Group under ZiPack)")
        self.chk_cascaded.setChecked(True)
        self.chk_cascaded.toggled.connect(self._on_cascaded_toggled)
        t1_layout.addWidget(self.chk_cascaded)

        self.lbl_preview_content = QLabel("Preview: ZiPack > Extract here | Extract to subfolder | Add...")
        t1_layout.addWidget(self.lbl_preview_content)
        t1_layout.addStretch()
        self.tabs.addTab(tab1, "Context Menu")

        # Tab 2: File Associations
        tab2 = QWidget()
        t2_layout = QVBoxLayout(tab2)
        grid = QGridLayout()
        self.ext_checkboxes = {}
        for idx, ext in enumerate(ShellIntegration.SUPPORTED_EXTS):
            chk = QCheckBox(ext)
            chk.setChecked(True)
            self.ext_checkboxes[ext] = chk
            grid.addWidget(chk, idx // 3, idx % 3)
        t2_layout.addLayout(grid)

        btn_box = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_all.clicked.connect(self._select_all_exts)
        btn_common = QPushButton("Select Common")
        btn_common.clicked.connect(self._select_common_exts)
        btn_none = QPushButton("Clear All")
        btn_none.clicked.connect(self._clear_all_exts)
        btn_box.addWidget(btn_all)
        btn_box.addWidget(btn_common)
        btn_box.addWidget(btn_none)
        t2_layout.addLayout(btn_box)
        self.tabs.addTab(tab2, "File Associations")

        # Tab 3: Shortcuts & Options
        tab3 = QWidget()
        t3_layout = QVBoxLayout(tab3)
        t3_layout.addWidget(QLabel("Create quick-launch shortcuts for ZiPack:"))
        self.chk_desktop_shortcut = QCheckBox("Create Desktop Shortcut")
        self.chk_desktop_shortcut.setChecked(True)
        self.chk_startmenu_shortcut = QCheckBox("Create Start Menu Shortcut")
        self.chk_startmenu_shortcut.setChecked(True)
        t3_layout.addWidget(self.chk_desktop_shortcut)
        t3_layout.addWidget(self.chk_startmenu_shortcut)

        btn_shortcuts = QPushButton("Create Shortcuts Now")
        btn_shortcuts.clicked.connect(self._create_shortcuts)
        t3_layout.addWidget(btn_shortcuts)
        t3_layout.addStretch()
        self.tabs.addTab(tab3, "Shortcuts")

        # Action footer
        footer = QHBoxLayout()
        self.btn_remove = QPushButton("Remove Integration")
        self.btn_remove.setProperty("variant", "danger")
        self.btn_remove.clicked.connect(self._remove_integration)
        footer.addWidget(self.btn_remove)

        footer.addStretch()

        self.btn_apply = QPushButton("Apply Integration")
        self.btn_apply.setProperty("variant", "primary")
        self.btn_apply.clicked.connect(self._apply_integration)
        footer.addWidget(self.btn_apply)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        main_layout.addLayout(footer)

    def _on_cascaded_toggled(self, checked: bool):
        if checked:
            self.lbl_preview_content.setText("Preview: ZiPack > Extract here | Extract to subfolder | Add...")
        else:
            self.lbl_preview_content.setText("Preview: Flat Context Menu entries")

    def _clear_all_exts(self):
        for chk in self.ext_checkboxes.values():
            chk.setChecked(False)

    def _select_common_exts(self):
        self._clear_all_exts()
        for ext in [".zip", ".7z", ".rar"]:
            if ext in self.ext_checkboxes:
                self.ext_checkboxes[ext].setChecked(True)

    def _select_all_exts(self):
        for chk in self.ext_checkboxes.values():
            chk.setChecked(True)

    def _get_current_config(self) -> dict:
        return {
            "cascaded": self.chk_cascaded.isChecked(),
            "extensions": [ext for ext, chk in self.ext_checkboxes.items() if chk.isChecked()],
            "enable_open": True,
            "enable_add_zip": True,
        }

    def _apply_integration(self):
        cfg = self._get_current_config()
        ok, msg = ShellIntegration.register_associations(cfg)
        if ok:
            self.lbl_status.setText("Current Shell Status: <b>Active (Registered in HKCU)</b>")
            QMessageBox.information(self, "Shell Integration", msg)
        else:
            QMessageBox.warning(self, "Shell Integration", msg)

    def _remove_integration(self):
        ok, msg = ShellIntegration.unregister_associations()
        if ok:
            self.lbl_status.setText("Current Shell Status: <b>Not Registered</b>")
            QMessageBox.information(self, "Shell Integration", msg)
        else:
            QMessageBox.warning(self, "Shell Integration", msg)

    def _create_shortcuts(self):
        ok, msg = ShellIntegration.create_shortcuts(
            desktop=self.chk_desktop_shortcut.isChecked(),
            start_menu=self.chk_startmenu_shortcut.isChecked(),
        )
        if ok:
            QMessageBox.information(self, "Shortcuts", msg)
        else:
            QMessageBox.warning(self, "Shortcuts", msg)
