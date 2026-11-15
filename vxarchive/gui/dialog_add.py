"""
Add to Archive Dialog for VXArchive.
Full-featured archive creation dialog supporting format selection (ZIP, 7Z, TAR),
compression levels, AES-256 encryption, split volumes, and file curation.
"""
import os
from typing import List, Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QGroupBox, QFileDialog,
    QMessageBox, QListWidget, QListWidgetItem, QToolButton,
    QTabWidget, QWidget, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .icons import IconEngine


class ArchiveNameAndParametersDialog(QDialog):
    def __init__(self, parent=None, default_archive_name: str = "archive.zip", files_to_add: Optional[List[str]] = None):
        super().__init__(parent)
        self.setWindowTitle("Add to Archive - VXArchive")
        self.resize(540, 520)
        self.setMinimumWidth(500)

        self.files_to_add: List[str] = [os.path.abspath(f) for f in (files_to_add or []) if os.path.exists(f)]

        # Determine smart initial archive output location
        if self.files_to_add:
            first_item = self.files_to_add[0]
            parent_dir = os.path.dirname(first_item)
            base_name = os.path.splitext(os.path.basename(first_item))[0] if len(self.files_to_add) == 1 else "Archive"
            initial_output = os.path.join(parent_dir, f"{base_name}.zip")
        else:
            initial_output = os.path.abspath(default_archive_name)

        self._setup_ui(initial_output)

    def _setup_ui(self, initial_output: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        # Tab widget for organized configuration
        self.tabs = QTabWidget()
        tabs = self.tabs

        # Tab 1: General & Compression
        tab_general = QWidget()
        gen_layout = QVBoxLayout(tab_general)
        gen_layout.setSpacing(12)

        # Output Archive Path & Browse
        lbl_dest = QLabel("Archive output path:")
        lbl_dest.setStyleSheet("font-weight: 600; color: #f1f5f9; font-size: 13px;")
        gen_layout.addWidget(lbl_dest)

        dest_box = QHBoxLayout()
        dest_box.setSpacing(8)

        self.name_input = QLineEdit(initial_output)
        self.name_input.setPlaceholderText("Select output archive file path...")
        self.name_input.setMinimumHeight(32)
        dest_box.addWidget(self.name_input, 1)

        self.btn_browse = QPushButton(" Browse...")
        self.btn_browse.setIcon(IconEngine.get_icon("folder", 16))
        self.btn_browse.setMinimumHeight(32)
        self.btn_browse.clicked.connect(self._on_browse_output)
        dest_box.addWidget(self.btn_browse)
        gen_layout.addLayout(dest_box)

        # Archive Format & Level Group
        grp_format = QGroupBox("Format & Compression Settings")
        grp_layout = QVBoxLayout(grp_format)
        grp_layout.setSpacing(10)

        # Format selector
        row_fmt = QHBoxLayout()
        row_fmt.addWidget(QLabel("Archive format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["ZIP (Universal Compatibility)", "7Z (High Compression Ratio)", "TAR (POSIX Container)"])
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        row_fmt.addWidget(self.format_combo, 1)
        grp_layout.addLayout(row_fmt)

        # Compression level selector
        row_level = QHBoxLayout()
        row_level.addWidget(QLabel("Compression level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems([
            "Store (No compression, fastest)",
            "Fast (Quick packaging)",
            "Normal (Recommended balance)",
            "Maximum (Smaller size)",
            "Ultra (Maximum ratio, heavy CPU)"
        ])
        self.level_combo.setCurrentIndex(2)  # Normal
        row_level.addWidget(self.level_combo, 1)
        grp_layout.addLayout(row_level)

        # Split into volumes
        row_split = QHBoxLayout()
        row_split.addWidget(QLabel("Split into volumes:"))
        self.split_combo = QComboBox()
        self.split_combo.addItems([
            "No splitting (Single archive file)",
            "10 MB (Small email chunks)",
            "100 MB (Standard web chunks)",
            "700 MB (CD-R)",
            "4300 MB (DVD-R)",
            "Custom size in MB..."
        ])
        self.split_combo.currentIndexChanged.connect(self._on_split_changed)
        row_split.addWidget(self.split_combo, 1)

        self.spin_custom_split = QSpinBox()
        self.spin_custom_split.setRange(1, 100000)
        self.spin_custom_split.setValue(50)
        self.spin_custom_split.setSuffix(" MB")
        self.spin_custom_split.setVisible(False)
        row_split.addWidget(self.spin_custom_split)
        grp_layout.addLayout(row_split)

        gen_layout.addWidget(grp_format)
        gen_layout.addStretch()
        tabs.addTab(tab_general, "General & Compression")

        # Tab 2: Security & Password
        tab_sec = QWidget()
        sec_layout = QVBoxLayout(tab_sec)
        sec_layout.setSpacing(12)

        grp_pwd = QGroupBox("AES-256 Encryption")
        pwd_vbox = QVBoxLayout(grp_pwd)
        pwd_vbox.setSpacing(10)

        # Password input
        row_pwd1 = QHBoxLayout()
        lbl_p1 = QLabel("Enter password:")
        lbl_p1.setMinimumWidth(110)
        row_pwd1.addWidget(lbl_p1)
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Leave empty for no password...")
        self.pwd_input.setMinimumHeight(30)
        row_pwd1.addWidget(self.pwd_input, 1)

        self.btn_toggle_pwd = QToolButton()
        self.btn_toggle_pwd.setIcon(IconEngine.get_icon("view", 16))
        self.btn_toggle_pwd.setCheckable(True)
        self.btn_toggle_pwd.setToolTip("Show/Hide password")
        self.btn_toggle_pwd.toggled.connect(self._toggle_pwd_visibility)
        row_pwd1.addWidget(self.btn_toggle_pwd)
        pwd_vbox.addLayout(row_pwd1)

        # Confirm password
        row_pwd2 = QHBoxLayout()
        lbl_p2 = QLabel("Confirm password:")
        lbl_p2.setMinimumWidth(110)
        row_pwd2.addWidget(lbl_p2)
        self.pwd_confirm = QLineEdit()
        self.pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_confirm.setPlaceholderText("Re-type password...")
        self.pwd_confirm.setMinimumHeight(30)
        row_pwd2.addWidget(self.pwd_confirm, 1)
        pwd_vbox.addLayout(row_pwd2)

        # Encrypt file names
        self.chk_encrypt_headers = QCheckBox("Encrypt file names (7Z format only)")
        self.chk_encrypt_headers.setChecked(True)
        pwd_vbox.addWidget(self.chk_encrypt_headers)

        sec_layout.addWidget(grp_pwd)
        sec_layout.addStretch()
        tabs.addTab(tab_sec, "Security & Encryption")

        # Tab 3: Files to Add
        tab_files = QWidget()
        files_layout = QVBoxLayout(tab_files)
        files_layout.setSpacing(8)

        files_layout.addWidget(QLabel("Selected items to package into archive:"))
        self.list_files = QListWidget()
        for f in self.files_to_add:
            item = QListWidgetItem(f)
            item.setIcon(IconEngine.get_icon("folder" if os.path.isdir(f) else "archive", 16))
            self.list_files.addItem(item)
        files_layout.addWidget(self.list_files, 1)

        files_btn_row = QHBoxLayout()
        btn_add_f = QPushButton("Add Files...")
        btn_add_f.clicked.connect(self._on_add_files)
        btn_add_d = QPushButton("Add Folder...")
        btn_add_d.clicked.connect(self._on_add_folder)
        btn_remove = QPushButton("Remove Selected")
        btn_remove.clicked.connect(self._on_remove_file)

        files_btn_row.addWidget(btn_add_f)
        files_btn_row.addWidget(btn_add_d)
        files_btn_row.addWidget(btn_remove)
        files_layout.addLayout(files_btn_row)

        tabs.addTab(tab_files, f"Files ({len(self.files_to_add)})")
        self.tabs = tabs
        layout.addWidget(tabs, 1)

        # Bottom Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.addStretch()

        self.btn_ok = QPushButton("Create Archive")
        self.btn_ok.setIcon(IconEngine.get_icon("add", 16))
        self.btn_ok.setMinimumHeight(34)
        self.btn_ok.setMinimumWidth(120)
        self.btn_ok.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: 600; border-radius: 6px;")
        self.btn_ok.clicked.connect(self._on_accept_clicked)
        self.btn_ok.setDefault(True)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setMinimumHeight(34)
        self.btn_cancel.setMinimumWidth(85)
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(self.btn_ok)
        btn_box.addWidget(self.btn_cancel)
        layout.addLayout(btn_box)

    def _on_browse_output(self):
        curr = self.name_input.text().strip()
        start_dir = os.path.dirname(curr) if curr else os.path.expanduser("~")
        fmt = self.get_format()
        filters = "ZIP Archive (*.zip);;7-Zip Archive (*.7z);;TAR Archive (*.tar);;All Files (*.*)"
        if fmt == "7z":
            filters = "7-Zip Archive (*.7z);;ZIP Archive (*.zip);;TAR Archive (*.tar);;All Files (*.*)"
        elif fmt == "tar":
            filters = "TAR Archive (*.tar);;ZIP Archive (*.zip);;7-Zip Archive (*.7z);;All Files (*.*)"

        path, _ = QFileDialog.getSaveFileName(self, "Save New Archive As", curr, filters)
        if path:
            self.name_input.setText(os.path.normpath(path))

    def _on_format_changed(self, idx: int):
        ext_map = {0: ".zip", 1: ".7z", 2: ".tar"}
        target_ext = ext_map.get(idx, ".zip")
        curr = self.name_input.text().strip()
        if curr:
            base, ext = os.path.splitext(curr)
            if ext.lower() in [".zip", ".7z", ".tar", ".gz", ".bz2", ".xz"]:
                self.name_input.setText(base + target_ext)

        # Enable/disable encrypt headers based on 7z format
        self.chk_encrypt_headers.setEnabled(idx == 1)

    def _on_split_changed(self, idx: int):
        self.spin_custom_split.setVisible(idx == 5)

    def _toggle_pwd_visibility(self, checked: bool):
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.pwd_input.setEchoMode(mode)
        self.pwd_confirm.setEchoMode(mode)

    def _on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Add", "", "All Files (*.*)")
        for f in files:
            p = os.path.abspath(f)
            if p not in self.files_to_add:
                self.files_to_add.append(p)
                item = QListWidgetItem(p)
                item.setIcon(IconEngine.get_icon("archive", 16))
                self.list_files.addItem(item)
        self.tabs.setTabText(2, f"Files ({len(self.files_to_add)})")

    def _on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Add")
        if folder:
            p = os.path.abspath(folder)
            if p not in self.files_to_add:
                self.files_to_add.append(p)
                item = QListWidgetItem(p)
                item.setIcon(IconEngine.get_icon("folder", 16))
                self.list_files.addItem(item)
        self.tabs.setTabText(2, f"Files ({len(self.files_to_add)})")

    def _on_remove_file(self):
        for item in self.list_files.selectedItems():
            p = item.text()
            if p in self.files_to_add:
                self.files_to_add.remove(p)
            self.list_files.takeItem(self.list_files.row(item))
        self.tabs.setTabText(2, f"Files ({len(self.files_to_add)})")

    def _on_accept_clicked(self):
        output = self.get_output_path()
        if not output:
            QMessageBox.warning(self, "Validation Error", "Please specify a destination archive path.")
            return

        p1 = self.pwd_input.text().strip()
        p2 = self.pwd_confirm.text().strip()
        if p1 and p1 != p2:
            QMessageBox.warning(self, "Password Mismatch", "The passwords you entered do not match. Please verify them.")
            return

        if not self.files_to_add:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one file or folder to add to the archive.")
            return

        self.accept()

    def get_output_path(self) -> str:
        return os.path.normpath(self.name_input.text().strip())

    def get_format(self) -> str:
        idx = self.format_combo.currentIndex()
        return ["zip", "7z", "tar"][idx]

    def get_compression_level(self) -> int:
        idx = self.level_combo.currentIndex()
        return [0, 1, 5, 7, 9][idx]

    def get_password(self) -> Optional[str]:
        p = self.pwd_input.text().strip()
        return p if p else None

    def get_split_volume(self) -> Optional[str]:
        idx = self.split_combo.currentIndex()
        if idx == 0:
            return None
        elif idx == 1:
            return "10m"
        elif idx == 2:
            return "100m"
        elif idx == 3:
            return "700m"
        elif idx == 4:
            return "4300m"
        elif idx == 5:
            return f"{self.spin_custom_split.value()}m"
        return None

    def should_encrypt_headers(self) -> bool:
        return self.chk_encrypt_headers.isChecked()

    def get_files_to_add(self) -> List[str]:
        return list(self.files_to_add)
