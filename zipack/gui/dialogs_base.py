"""
Core modal dialogs for ZiPack: Add, Extract, View, Info, Benchmark, About, Eval, Find, Wizard, Password, Progress, Hash, Duplicates, Batch.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QProgressBar, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QAbstractItemView, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont
from ..core.archive_engine import ArchiveEngine
from ..core.benchmark import ZiPackBenchmark
from ..core.hasher import HashEngine
from ..core.dedup_analyzer import DuplicateAnalyzer
from ..core.batch_processor import BatchProcessor
from ..core.license_manager import LicenseManager
from ..core.utils import format_size

from .dialog_add import ArchiveNameAndParametersDialog
from .dialog_extract import ExtractionPathAndOptionsDialog


class InternalViewerDialog(QDialog):
    def __init__(self, parent=None, title="Viewer", data=b""):
        super().__init__(parent)
        self.setWindowTitle(f"Viewer - {title}")
        self.resize(580, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        try:
            self.text_edit.setPlainText(data.decode("utf-8", errors="replace"))
        except Exception:
            self.text_edit.setPlainText(str(data))
        layout.addWidget(self.text_edit, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


class ArchiveInfoDialog(QDialog):
    def __init__(self, parent=None, info=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Information")
        self.resize(440, 320)
        self.info = info or {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.table = QTableWidget(len(self.info), 2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        for i, (k, v) in enumerate(self.info.items()):
            self.table.setItem(i, 0, QTableWidgetItem(str(k)))
            self.table.setItem(i, 1, QTableWidgetItem(str(v)))
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


class BenchmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Compression Benchmark")
        self.resize(460, 260)
        self.benchmark = ZiPackBenchmark()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(QLabel("<b>Multi-Core Compression & Hashing Throughput</b>"))
        self.lbl_speed = QLabel("Throughput: 0.00 MB/s")
        self.lbl_speed.setStyleSheet("font-size: 20px; font-weight: 700; color: #38bdf8;")
        layout.addWidget(self.lbl_speed)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        layout.addStretch()

        btn_row = QHBoxLayout()
        self.btn_toggle = QPushButton("Start Benchmark")
        self.btn_toggle.setProperty("variant", "primary")
        self.btn_toggle.clicked.connect(self._toggle)
        btn_row.addWidget(self.btn_toggle)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)

    def _toggle(self):
        if not self.benchmark.running:
            self.benchmark.start()
            self.btn_toggle.setText("Stop Benchmark")
            self.progress.setVisible(True)
            self.timer.start(100)
        else:
            self.benchmark.stop()
            self.btn_toggle.setText("Start Benchmark")
            self.progress.setVisible(False)
            self.timer.stop()

    def _update(self):
        self.lbl_speed.setText(f"Throughput: {self.benchmark.speed_mb_per_sec:.2f} MB/s")

    def closeEvent(self, e):
        if self.benchmark.running:
            self.benchmark.stop()
        super().closeEvent(e)


class AboutZiPackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ZiPack")
        self.resize(420, 280)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        ico_label = QLabel()
        ico_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for cand in [
            os.path.join(base_dir, "zipack.ico"),
            os.path.join(os.path.dirname(base_dir), "zipack.ico"),
            os.path.join(getattr(sys, "_MEIPASS", ""), "zipack.ico") if getattr(sys, "frozen", False) else "",
            os.path.join(os.path.dirname(sys.executable), "zipack.ico") if getattr(sys, "frozen", False) else "",
            "zipack.ico",
        ]:
            if cand and os.path.isfile(cand):
                pix = QPixmap(cand).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                ico_label.setPixmap(pix)
                self.setWindowIcon(QIcon(cand))
                break
        layout.addWidget(ico_label)

        lbl = QLabel(
            "<h2>ZiPack</h2>"
            "<p style='color: #38bdf8; font-weight: 600;'>Next-Gen Archive Manager</p>"
            "<p>Version 2.5 (Windows 11 Fluent Edition)</p>"
            "<p style='color: #94a3b8; font-size: 11px;'>PyQt6 • Native C++/C#/C Acceleration • 7-Zip Engine</p>"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)


AboutVXArchiveDialog = AboutZiPackDialog


class EvaluationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ZiPack License & Registration")
        self.resize(440, 230)
        self.lic = LicenseManager.get_instance()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.lbl_status = QLabel()
        self._refresh_status()
        layout.addWidget(self.lbl_status)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Registered User / Organization")
        layout.addWidget(self.user_input)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("License Key (e.g. ZIPACK-PRO-XXXX)")
        layout.addWidget(self.key_input)

        btn_row = QHBoxLayout()
        self.btn_register = QPushButton("Activate License")
        self.btn_register.setProperty("variant", "primary")
        self.btn_register.clicked.connect(self._register)
        btn_row.addWidget(self.btn_register)

        self.btn_unregister = QPushButton("Reset")
        self.btn_unregister.clicked.connect(self._unregister)
        btn_row.addWidget(self.btn_unregister)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _refresh_status(self):
        if self.lic.is_registered:
            self.lbl_status.setText(f"<b>Status:</b> Licensed to <span style='color:#34d399'>{self.lic.registered_to}</span>")
        else:
            self.lbl_status.setText("<b>Status:</b> Evaluation / Free Edition — Thank you for using ZiPack!")

    def _register(self):
        user = self.user_input.text().strip()
        key = self.key_input.text().strip()
        if not user or not key:
            QMessageBox.warning(self, "Validation", "Please enter both a name and a license key.")
            return
        if self.lic.register(user, key):
            self._refresh_status()
            QMessageBox.information(self, "License Activated", f"Registered to {user}.")

    def _unregister(self):
        self.lic.unregister()
        self._refresh_status()


class FindFilesDialog(QDialog):
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        self.setWindowTitle("Find Files")
        self.resize(520, 360)
        self.items = items or []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file names...")
        self.search_input.textChanged.connect(self._filter)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["File Name", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

        self._filter("")

    def _filter(self, query: str):
        q = query.strip().lower()
        self.table.setRowCount(0)
        for it in self.items:
            name = getattr(it, "name", None) or (it.get("name", "") if isinstance(it, dict) else str(it))
            size = getattr(it, "size", None) if hasattr(it, "size") else (it.get("size", 0) if isinstance(it, dict) else 0)
            if not q or q in name.lower():
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(name))
                self.table.setItem(r, 1, QTableWidgetItem(format_size(size)))


class WizardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Wizard")
        self.resize(460, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Step 1: Choose an operation</b>"))

        actions = [
            ("Create a new archive...", "_action_add"),
            ("Extract an existing archive...", "_action_extract"),
            ("Repair a damaged archive...", "_action_repair"),
            ("Sanitize & optimize an archive...", "_action_sanitizer"),
        ]
        for label, method in actions:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, m=method: self._launch(m))
            layout.addWidget(btn)

        layout.addStretch()
        btn_close = QPushButton("Cancel")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def _launch(self, method_name: str):
        p = self.parent()
        self.accept()
        if p and hasattr(p, method_name):
            getattr(p, method_name)()


class PasswordDialog(QDialog):
    def __init__(self, parent=None, is_prompt_mode=False, archive_name=""):
        super().__init__(parent)
        self.setWindowTitle("Enter Password" if is_prompt_mode else "Password Options")
        self.resize(400, 210)
        self.is_prompt_mode = is_prompt_mode

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Enter archive password:"))
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pwd_input)

        if is_prompt_mode:
            self.remember_file_chk = QCheckBox("Remember password for this file")
            layout.addWidget(self.remember_file_chk)

            from ..core.password_memory import ArchivePasswordMemory
            mem = ArchivePasswordMemory.get_instance()
            cands = mem.extract_pattern_candidates(archive_name)
            pat_text = f"Remember for series ({cands[0]})" if cands else "Remember for series"
            self.remember_pattern_chk = QCheckBox(pat_text)
            layout.addWidget(self.remember_pattern_chk)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("OK")
        btn_ok.setProperty("variant", "primary")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_ok)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)


class ZiPackProgressDialog(QDialog):
    def __init__(self, parent=None, title="Operation in Progress", operation_type="Processing"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(420, 160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.lbl_status = QLabel(f"{operation_type}...")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)


VXArchiveProgressDialog = ZiPackProgressDialog


class HashInspectorDialog(QDialog):
    def __init__(self, parent=None, file_path_or_data=b"", display_name="sample.txt"):
        super().__init__(parent)
        self.setWindowTitle(f"Checksum Inspector - {display_name}")
        self.resize(580, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.table = QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["Algorithm", "Hash Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        self._populate_hashes(file_path_or_data)
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_file = QPushButton("Inspect File...")
        btn_file.clicked.connect(self._browse_file)
        btn_row.addWidget(btn_file)

        btn_copy = QPushButton("Copy SHA-256")
        btn_copy.clicked.connect(self._copy_sha256)
        btn_row.addWidget(btn_copy)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _populate_hashes(self, source):
        if isinstance(source, str) and os.path.isfile(source):
            hashes = HashEngine.calculate_hashes(source)
        else:
            import hashlib
            import zlib
            raw = bytes(source) if isinstance(source, (bytes, bytearray)) else b""
            hashes = {
                "CRC32": f"{zlib.crc32(raw) & 0xFFFFFFFF:08X}",
                "MD5": hashlib.md5(raw).hexdigest().upper(),
                "SHA-1": hashlib.sha1(raw).hexdigest().upper(),
                "SHA-256": hashlib.sha256(raw).hexdigest().upper(),
                "SHA-512": hashlib.sha512(raw).hexdigest().upper(),
            }

        algos = [
            ("CRC32", hashes.get("CRC32", hashes.get("crc32", ""))),
            ("MD5", hashes.get("MD5", hashes.get("md5", ""))),
            ("SHA-1", hashes.get("SHA-1", hashes.get("sha1", ""))),
            ("SHA-256", hashes.get("SHA-256", hashes.get("sha256", ""))),
            ("SHA-512", hashes.get("SHA-512", hashes.get("sha512", ""))),
        ]
        for i, (a, h) in enumerate(algos):
            self.table.setItem(i, 0, QTableWidgetItem(a))
            self.table.setItem(i, 1, QTableWidgetItem(h))

    def _browse_file(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select File to Hash")
        if fp:
            self.setWindowTitle(f"Checksum Inspector - {os.path.basename(fp)}")
            self._populate_hashes(fp)

    def _copy_sha256(self):
        item = self.table.item(3, 1)
        if item:
            QApplication.clipboard().setText(item.text())
            QMessageBox.information(self, "Copied", "SHA-256 hash copied to clipboard.")


class DuplicateAnalyzerDialog(QDialog):
    def __init__(self, parent=None, archive_items=None, title="Duplicate Analyzer", initial_folder=None):
        super().__init__(parent)
        self.setWindowTitle(f"Duplicate Analyzer - {title}")
        self.resize(600, 380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.lbl_summary = QLabel("Duplicate Files & Storage Waste:")
        layout.addWidget(self.lbl_summary)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File Name", "Size", "Duplicate Group"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        items = archive_items or []
        if items:
            result = DuplicateAnalyzer.analyze_archive_items(items)
            groups = result.get("duplicate_groups", [])
            wasted = result.get("wasted_bytes", 0)
            self.lbl_summary.setText(
                f"Found <b>{len(groups)}</b> duplicate group(s) — Potential savings: <b>{format_size(wasted)}</b>"
            )
            for idx, grp in enumerate(groups, 1):
                for member in grp.get("files", []):
                    r = self.table.rowCount()
                    self.table.insertRow(r)
                    self.table.setItem(r, 0, QTableWidgetItem(str(member)))
                    self.table.setItem(r, 1, QTableWidgetItem(format_size(grp.get("size", 0))))
                    self.table.setItem(r, 2, QTableWidgetItem(f"Group #{idx}"))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


class BatchManagerDialog(QDialog):
    def __init__(self, parent=None, initial_archives=None, initial_sources=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Multi-Archive Manager")
        self.resize(580, 420)
        self.engine = ArchiveEngine()
        self.batch = BatchProcessor(self.engine)
        self.archives = list(initial_archives or [])
        self.sources = list(initial_sources or [])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Batch Archive Processing Queue</b>"))

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Item Path", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel("Output Folder:"))
        self.dest_input = QLineEdit(os.path.expanduser("~\\Downloads"))
        dest_row.addWidget(self.dest_input, 1)
        btn_dest = QPushButton("Browse...")
        btn_dest.clicked.connect(self._browse_dest)
        dest_row.addWidget(btn_dest)
        layout.addLayout(dest_row)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Archives...")
        btn_add.clicked.connect(self._add_archives)
        btn_row.addWidget(btn_add)

        btn_extract = QPushButton("Batch Extract All")
        btn_extract.setProperty("variant", "primary")
        btn_extract.clicked.connect(self._run_batch_extract)
        btn_row.addWidget(btn_extract)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self._refresh_table()

    def _browse_dest(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.dest_input.text())
        if d:
            self.dest_input.setText(d)

    def _add_archives(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Archives", "", "Archive Files (*.zip *.rar *.7z *.tar *.gz);;All Files (*.*)"
        )
        for f in files:
            if f not in self.archives:
                self.archives.append(f)
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(0)
        for a in self.archives:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(a))
            self.table.setItem(r, 1, QTableWidgetItem("Queued"))

    def _run_batch_extract(self):
        if not self.archives:
            QMessageBox.information(self, "Batch Extract", "Please add one or more archives first.")
            return
        dest = self.dest_input.text().strip() or os.getcwd()
        results = self.batch.batch_extract(self.archives, dest, into_subfolders=True)
        for idx, (_, ok, msg) in enumerate(results):
            if idx < self.table.rowCount():
                self.table.setItem(idx, 1, QTableWidgetItem("OK" if ok else f"Failed: {msg}"))
        QMessageBox.information(self, "Batch Complete", f"Processed {len(results)} archive(s).")
