"""
Extraction Path and Options Dialog for VXArchive.
Allows user to specify destination directory, browse via native folder picker,
extract to subfolder, configure overwrite behaviors, and supply password.
"""
import os
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QGroupBox, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .icons import IconEngine


class ExtractionPathAndOptionsDialog(QDialog):
    def __init__(self, parent=None, default_dest: str = "", default_archive: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Extract Archive - VXArchive")
        self.resize(500, 310)
        self.setMinimumWidth(460)

        self.default_archive = default_archive or ""
        # Determine smart initial destination folder
        if default_dest and os.path.exists(default_dest) and default_dest.lower() != "c:\\temp":
            initial_dest = default_dest
        elif self.default_archive and os.path.isfile(self.default_archive):
            initial_dest = os.path.dirname(os.path.abspath(self.default_archive))
        elif os.path.exists(os.path.expanduser("~\\Downloads")):
            initial_dest = os.path.expanduser("~\\Downloads")
        elif os.path.exists(os.path.expanduser("~\\Desktop")):
            initial_dest = os.path.expanduser("~\\Desktop")
        else:
            initial_dest = default_dest or os.path.expanduser("~")

        self.subfolder_name = ""
        if self.default_archive:
            base = os.path.basename(self.default_archive)
            self.subfolder_name = os.path.splitext(base)[0]

        self._setup_ui(initial_dest)

    def _setup_ui(self, initial_dest: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        # 1. Destination Section
        lbl_dest = QLabel("Extract to destination folder:")
        lbl_dest.setStyleSheet("font-weight: 600; color: #f1f5f9; font-size: 13px;")
        layout.addWidget(lbl_dest)

        dest_box = QHBoxLayout()
        dest_box.setSpacing(8)

        self.dest_input = QLineEdit(initial_dest)
        self.dest_input.setPlaceholderText("Select extraction target directory...")
        self.dest_input.setMinimumHeight(34)
        dest_box.addWidget(self.dest_input, 1)

        self.btn_browse = QPushButton(" Browse...")
        self.btn_browse.setIcon(IconEngine.get_icon("folder", 16))
        self.btn_browse.setMinimumHeight(34)
        self.btn_browse.setMinimumWidth(95)
        self.btn_browse.setToolTip("Browse and select destination folder (Ctrl+B)")
        self.btn_browse.clicked.connect(self._on_browse)
        dest_box.addWidget(self.btn_browse)

        layout.addLayout(dest_box)

        # 2. Options Group
        opts_group = QGroupBox("Extraction Options")
        opts_layout = QVBoxLayout(opts_group)
        opts_layout.setSpacing(8)
        opts_layout.setContentsMargins(12, 14, 12, 12)

        subfolder_label = f"Extract to subfolder '{self.subfolder_name}'" if self.subfolder_name else "Extract to subfolder named after archive"
        self.chk_subfolder = QCheckBox(subfolder_label)
        self.chk_subfolder.setChecked(bool(self.subfolder_name))
        opts_layout.addWidget(self.chk_subfolder)

        self.chk_open_folder = QCheckBox("Open destination folder when extraction finishes")
        self.chk_open_folder.setChecked(True)
        opts_layout.addWidget(self.chk_open_folder)

        self.chk_overwrite = QCheckBox("Overwrite existing files without prompting")
        self.chk_overwrite.setChecked(False)
        opts_layout.addWidget(self.chk_overwrite)

        layout.addWidget(opts_group)

        # 3. Password Box (Optional)
        pwd_box = QHBoxLayout()
        pwd_box.setSpacing(8)
        lbl_pwd = QLabel("Password:")
        lbl_pwd.setStyleSheet("color: #94a3b8;")
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Leave blank if archive is not encrypted")
        self.pwd_input.setMinimumHeight(30)

        self.btn_toggle_pwd = QToolButton()
        self.btn_toggle_pwd.setIcon(IconEngine.get_icon("view", 16))
        self.btn_toggle_pwd.setCheckable(True)
        self.btn_toggle_pwd.setToolTip("Show/Hide password")
        self.btn_toggle_pwd.toggled.connect(self._toggle_pwd_visibility)
        self.btn_toggle_pwd.setMinimumHeight(30)

        pwd_box.addWidget(lbl_pwd)
        pwd_box.addWidget(self.pwd_input, 1)
        pwd_box.addWidget(self.btn_toggle_pwd)
        layout.addLayout(pwd_box)

        # 4. Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.addStretch()

        self.btn_ok = QPushButton("Extract")
        self.btn_ok.setIcon(IconEngine.get_icon("extract", 16))
        self.btn_ok.setMinimumHeight(34)
        self.btn_ok.setMinimumWidth(100)
        self.btn_ok.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: 600; border-radius: 6px;")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setMinimumHeight(34)
        self.btn_cancel.setMinimumWidth(85)
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(self.btn_ok)
        btn_box.addWidget(self.btn_cancel)
        layout.addLayout(btn_box)

    def _on_browse(self):
        curr = self.dest_input.text().strip()
        if not curr or not os.path.isdir(curr):
            if self.default_archive and os.path.isfile(self.default_archive):
                curr = os.path.dirname(os.path.abspath(self.default_archive))
            else:
                curr = os.path.expanduser("~")
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Destination Folder", curr)
        if selected_dir:
            self.dest_input.setText(os.path.normpath(selected_dir))

    def _toggle_pwd_visibility(self, checked: bool):
        if checked:
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)

    def get_destination_path(self) -> str:
        base_dir = self.dest_input.text().strip() or os.getcwd()
        base_dir = os.path.normpath(base_dir)
        if self.chk_subfolder.isChecked() and self.subfolder_name:
            return os.path.join(base_dir, self.subfolder_name)
        return base_dir

    def get_password(self) -> Optional[str]:
        pwd = self.pwd_input.text().strip()
        return pwd if pwd else None

    def should_open_folder(self) -> bool:
        return self.chk_open_folder.isChecked()

    def should_overwrite(self) -> bool:
        return self.chk_overwrite.isChecked()
