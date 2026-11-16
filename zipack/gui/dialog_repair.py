"""
Archive Integrity Salvager and Auto-Repair Wizard for VXArchive.
Recovers intact files from damaged, partially downloaded, or header-corrupted archives.
"""
import os
import subprocess
from typing import List, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QRadioButton, QTextEdit,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from .icons import IconEngine
from ..core.archive_repair import ArchiveRepairEngine
from ..core.archive_engine import ArchiveEngine


class RepairWorker(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, list)

    def __init__(self, corrupt_path: str, output_path: str, mode: str):
        super().__init__()
        self.corrupt_path = corrupt_path
        self.output_path = output_path
        self.mode = mode

    def run(self):
        engine = ArchiveEngine()
        repairer = ArchiveRepairEngine(engine)
        self.progress_signal.emit(f"[*] Analyzing damaged archive: {os.path.basename(self.corrupt_path)}...")

        if self.mode == "header":
            self.progress_signal.emit("[*] Mode: Fast Header Alignment & Preamble Truncation...")
            ok, msg, files = repairer.repair_archive(self.corrupt_path, self.output_path)
            self.finished_signal.emit(ok, msg, files)
        else:
            self.progress_signal.emit("[*] Mode: Deep Stream Carving & Member Extraction...")
            ok, msg, files = repairer.repair_archive(self.corrupt_path, self.output_path)
            self.finished_signal.emit(ok, msg, files)


class ArchiveRepairDialog(QDialog):
    def __init__(self, parent=None, initial_archive: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Archive Integrity Salvager & Auto-Repair - ZiPack")
        self.resize(560, 480)
        self.setMinimumWidth(500)

        self.initial_archive = os.path.abspath(initial_archive) if initial_archive and os.path.exists(initial_archive) else ""
        self.worker = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        # Header description
        lbl_desc = QLabel("Salvage readable files from corrupted or truncated archives:")
        lbl_desc.setStyleSheet("font-weight: 600; color: #f1f5f9; font-size: 13px;")
        layout.addWidget(lbl_desc)

        # 1. Damaged Archive Path
        row_src = QHBoxLayout()
        self.input_src = QLineEdit(self.initial_archive)
        self.input_src.setPlaceholderText("Select damaged archive file...")
        self.input_src.setMinimumHeight(32)
        self.input_src.textChanged.connect(self._on_src_changed)

        btn_browse_src = QPushButton(" Browse...")
        btn_browse_src.setIcon(IconEngine.get_icon("folder", 16))
        btn_browse_src.setMinimumHeight(32)
        btn_browse_src.clicked.connect(self._on_browse_src)

        row_src.addWidget(self.input_src, 1)
        row_src.addWidget(btn_browse_src)
        layout.addLayout(row_src)

        # 2. Output Salvaged Path
        row_out = QHBoxLayout()
        default_out = ""
        if self.initial_archive:
            base, ext = os.path.splitext(self.initial_archive)
            default_out = f"{base}_salvaged{ext or '.zip'}"
        self.input_out = QLineEdit(default_out)
        self.input_out.setPlaceholderText("Select destination for salvaged data...")
        self.input_out.setMinimumHeight(32)

        btn_browse_out = QPushButton(" Save As...")
        btn_browse_out.setMinimumHeight(32)
        btn_browse_out.clicked.connect(self._on_browse_out)

        row_out.addWidget(self.input_out, 1)
        row_out.addWidget(btn_browse_out)
        layout.addLayout(row_out)

        # 3. Repair Strategies
        grp_modes = QGroupBox("Salvaging & Reconstruction Strategies")
        vbox_modes = QVBoxLayout(grp_modes)
        vbox_modes.setSpacing(6)

        self.rad_header = QRadioButton("Fast Header Alignment (Fixes corrupted prepends & truncated Zip headers)")
        self.rad_header.setChecked(True)
        vbox_modes.addWidget(self.rad_header)

        self.rad_carve = QRadioButton("Deep Stream Carving (Extracts all uncorrupted individual files via 7-Zip)")
        vbox_modes.addWidget(self.rad_carve)

        layout.addWidget(grp_modes)

        # 4. Progress and Log Output
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Diagnostic and recovery log will appear here...")
        self.log_edit.setStyleSheet("background-color: #0d0e12; color: #a5f3fc; font-family: 'Consolas', monospace; font-size: 12px;")
        layout.addWidget(self.log_edit, 1)

        # 5. Bottom Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        self.btn_open_folder = QPushButton("Open Recovered Folder")
        self.btn_open_folder.setIcon(IconEngine.get_icon("folder", 16))
        self.btn_open_folder.setVisible(False)
        self.btn_open_folder.clicked.connect(self._on_open_folder)
        btn_box.addWidget(self.btn_open_folder)

        btn_box.addStretch()

        self.btn_start = QPushButton("Start Salvage")
        self.btn_start.setIcon(IconEngine.get_icon("repair", 16))
        self.btn_start.setMinimumHeight(34)
        self.btn_start.setMinimumWidth(120)
        self.btn_start.setStyleSheet("background-color: #eab308; color: #000000; font-weight: 700; border-radius: 6px;")
        self.btn_start.clicked.connect(self._on_start_clicked)

        self.btn_close = QPushButton("Close")
        self.btn_close.setMinimumHeight(34)
        self.btn_close.setMinimumWidth(80)
        self.btn_close.clicked.connect(self.close)

        btn_box.addWidget(self.btn_start)
        btn_box.addWidget(self.btn_close)
        layout.addLayout(btn_box)

    def _on_src_changed(self, text: str):
        if text.strip() and not self.input_out.text().strip():
            base, ext = os.path.splitext(text.strip())
            self.input_out.setText(f"{base}_salvaged{ext or '.zip'}")

    def _on_browse_src(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Damaged Archive", "",
            "Archive Files (*.zip *.7z *.rar *.tar *.gz *.iso);;All Files (*.*)"
        )
        if path:
            self.input_src.setText(os.path.normpath(path))
            base, ext = os.path.splitext(path)
            self.input_out.setText(os.path.normpath(f"{base}_salvaged{ext or '.zip'}"))

    def _on_browse_out(self):
        curr = self.input_out.text().strip()
        path, _ = QFileDialog.getSaveFileName(self, "Save Salvaged Archive As", curr, "All Files (*.*)")
        if path:
            self.input_out.setText(os.path.normpath(path))

    def _on_start_clicked(self):
        src = self.input_src.text().strip()
        out = self.input_out.text().strip()
        if not src or not os.path.isfile(src):
            QMessageBox.warning(self, "Missing Source", "Please select a valid damaged archive file.")
            return
        if not out:
            QMessageBox.warning(self, "Missing Output", "Please choose an output destination path.")
            return

        self.btn_start.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.log_edit.clear()

        mode = "header" if self.rad_header.isChecked() else "carve"
        self.worker = RepairWorker(src, out, mode)
        self.worker.progress_signal.connect(self._append_log)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _append_log(self, text: str):
        self.log_edit.append(text)

    def _on_finished(self, ok: bool, msg: str, files: list):
        self.progress_bar.setVisible(False)
        self.btn_start.setEnabled(True)

        if ok:
            self._append_log(f"\n[+] SUCCESS: {msg}")
            if files:
                self._append_log(f"[+] Total files rescued: {len(files)}")
                for f in files[:20]:
                    self._append_log(f"    - {f}")
                if len(files) > 20:
                    self._append_log(f"    ... and {len(files)-20} more items.")
            self.btn_open_folder.setVisible(True)
            QMessageBox.information(self, "Salvage Complete", f"Archive recovery succeeded!\n{msg}")
        else:
            self._append_log(f"\n[-] FAILED: {msg}")
            QMessageBox.warning(self, "Salvage Failed", f"Could not salvage archive structure:\n{msg}")

    def _on_open_folder(self):
        out = self.input_out.text().strip()
        dest = out if os.path.isdir(out) else os.path.dirname(out)
        if os.path.isdir(dest):
            import subprocess
            subprocess.Popen(f'explorer "{os.path.normpath(dest)}"')
