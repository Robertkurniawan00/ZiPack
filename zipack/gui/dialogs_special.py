"""
Specialized dialogs: Grep, SFX, LAN Share, Missing Volume, Health, Diagnostic, Sanitizer.
"""
import os
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ..core.archive_engine import ArchiveEngine
from ..core.archive_grep import ArchiveGrepEngine
from ..core.sfx_builder import SFXBuilder
from ..core.lan_share import LANShareServer
from ..core.splitter import MultiVolumeDetector
from ..core.health_checker import ArchiveHealthChecker
from ..core.sanitizer import ArchiveSanitizer
from ..core.utils import format_size


class DeepGrepDialog(QDialog):
    def __init__(self, parent=None, archive_path=""):
        super().__init__(parent)
        self.setWindowTitle("Deep In-Archive Grep Search")
        self.resize(620, 400)
        self.grep = ArchiveGrepEngine()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        arc_row = QHBoxLayout()
        self.arc_input = QLineEdit(archive_path)
        self.arc_input.setPlaceholderText("Select archive to search inside...")
        arc_row.addWidget(self.arc_input, 1)
        btn_arc = QPushButton("Browse...")
        btn_arc.clicked.connect(self._browse)
        arc_row.addWidget(btn_arc)
        layout.addLayout(arc_row)

        q_row = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter text or regex query...")
        self.query_input.returnPressed.connect(self._search)
        q_row.addWidget(self.query_input, 1)

        self.chk_regex = QCheckBox("Regex")
        q_row.addWidget(self.chk_regex)

        btn_search = QPushButton("Search")
        btn_search.setProperty("variant", "primary")
        btn_search.clicked.connect(self._search)
        q_row.addWidget(btn_search)
        layout.addLayout(q_row)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File", "Line", "Matched Text"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Archive", "", "Archives (*.zip *.7z *.rar *.tar);;All Files (*.*)")
        if fp:
            self.arc_input.setText(fp)

    def _search(self):
        arc = self.arc_input.text().strip()
        q = self.query_input.text().strip()
        if not os.path.isfile(arc) or not q:
            return
        matches = self.grep.search(arc, q, is_regex=self.chk_regex.isChecked())
        self.table.setRowCount(0)
        for m in matches:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(m.filename))
            self.table.setItem(r, 1, QTableWidgetItem(str(m.line_number)))
            self.table.setItem(r, 2, QTableWidgetItem(m.line_text))


class SFXStudioDialog(QDialog):
    def __init__(self, parent=None, initial_source=""):
        super().__init__(parent)
        self.setWindowTitle("Standalone SFX Studio")
        self.resize(500, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Compile standalone self-extracting .exe archive:</b>"))

        src_row = QHBoxLayout()
        self.src_input = QLineEdit(initial_source)
        self.src_input.setPlaceholderText("Source archive (.7z / .zip)...")
        src_row.addWidget(self.src_input, 1)
        btn_src = QPushButton("Browse...")
        btn_src.clicked.connect(self._browse)
        src_row.addWidget(btn_src)
        layout.addLayout(src_row)

        layout.addStretch()
        btn_row = QHBoxLayout()
        btn_build = QPushButton("Build SFX .exe")
        btn_build.setProperty("variant", "primary")
        btn_build.clicked.connect(self._build)
        btn_row.addWidget(btn_build)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Source Archive", "", "Archives (*.7z *.zip);;All Files (*.*)")
        if fp:
            self.src_input.setText(fp)

    def _build(self):
        src = self.src_input.text().strip()
        if not os.path.isfile(src):
            QMessageBox.warning(self, "SFX Studio", "Please select a valid archive.")
            return
        out = os.path.splitext(src)[0] + "_sfx.exe"
        ok, msg = SFXBuilder.build_sfx(src, out)
        QMessageBox.information(self, "SFX Studio", msg) if ok else QMessageBox.warning(self, "SFX Studio", msg)


class LANShareDialog(QDialog):
    def __init__(self, parent=None, file_path=""):
        super().__init__(parent)
        self.setWindowTitle("Instant LAN Wireless Transfer")
        self.resize(460, 420)
        self.server = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Share archive over local Wi-Fi (QR Code & HTTP):</b>"))

        file_row = QHBoxLayout()
        self.file_input = QLineEdit(file_path)
        self.file_input.setPlaceholderText("Select file to share...")
        file_row.addWidget(self.file_input, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        file_row.addWidget(btn_browse)
        layout.addLayout(file_row)

        self.lbl_qr = QLabel("Click 'Start Share' to generate QR code")
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qr.setMinimumHeight(200)
        layout.addWidget(self.lbl_qr, 1)

        self.lbl_url = QLabel("")
        self.lbl_url.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.lbl_url)

        btn_row = QHBoxLayout()
        self.btn_toggle = QPushButton("Start Share")
        self.btn_toggle.setProperty("variant", "primary")
        self.btn_toggle.clicked.connect(self._toggle)
        btn_row.addWidget(self.btn_toggle)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select File to Share")
        if fp:
            self.file_input.setText(fp)

    def _toggle(self):
        if self.server is None:
            fp = self.file_input.text().strip()
            if not os.path.isfile(fp):
                QMessageBox.warning(self, "LAN Share", "Please select a valid file.")
                return
            self.server = LANShareServer(fp)
            url = self.server.start()
            self.lbl_url.setText(f"<a href='{url}' style='color:#38bdf8'>{url}</a>")
            self.btn_toggle.setText("Stop Share")
            self._render_qr(url)
        else:
            self.server.stop()
            self.server = None
            self.btn_toggle.setText("Start Share")
            self.lbl_url.setText("Server stopped.")

    def _render_qr(self, url: str):
        try:
            import io
            import qrcode
            img = qrcode.make(url)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            pix = QPixmap()
            pix.loadFromData(buf.getvalue())
            self.lbl_qr.setPixmap(pix.scaled(190, 190, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception:
            self.lbl_qr.setText(f"URL ready:\n{url}")

    def closeEvent(self, event):
        if self.server:
            self.server.stop()
            self.server = None
        super().closeEvent(event)


class MissingVolumeDialog(QDialog):
    def __init__(self, parent=None, volume_set=None, initial_file=""):
        super().__init__(parent)
        self.setWindowTitle("Missing Volume Chunk Locator")
        self.resize(520, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        vset = volume_set
        if vset is None and initial_file and os.path.isfile(initial_file):
            vset = MultiVolumeDetector.inspect_volume_set(initial_file)

        summary = "Multi-volume part status:"
        if vset:
            summary = f"Found {vset.found_count}/{vset.total_expected} part(s) — Missing: {len(vset.missing_parts)}"
        layout.addWidget(QLabel(f"<b>{summary}</b>"))

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Part #", "Expected Filename", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        if vset:
            for mp in vset.missing_parts:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(mp.part_number)))
                self.table.setItem(r, 1, QTableWidgetItem(mp.expected_name))
                self.table.setItem(r, 2, QTableWidgetItem("MISSING"))
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


class ArchiveHealthDialog(QDialog):
    def __init__(self, parent=None, archive_path=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Health Diagnostic")
        self.resize(640, 400)
        self.checker = ArchiveHealthChecker()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        row = QHBoxLayout()
        self.arc_input = QLineEdit(archive_path)
        self.arc_input.setPlaceholderText("Select archive to verify...")
        row.addWidget(self.arc_input, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)

        btn_check = QPushButton("Run Health Check")
        btn_check.setProperty("variant", "primary")
        btn_check.clicked.connect(self._run_check)
        row.addWidget(btn_check)
        layout.addLayout(row)

        self.lbl_summary = QLabel("Ready to scan archive integrity.")
        layout.addWidget(self.lbl_summary)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Status", "File", "Size", "CRC", "Offset", "Health"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

        if archive_path and os.path.isfile(archive_path):
            self._run_check()

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Archive", "", "Archives (*.zip *.7z *.rar *.tar);;All Files (*.*)")
        if fp:
            self.arc_input.setText(fp)
            self._run_check()

    def _run_check(self):
        arc = self.arc_input.text().strip()
        if not os.path.isfile(arc):
            return
        report = self.checker.check_health(arc)
        self.lbl_summary.setText(
            f"<b>Status:</b> {report.overall_status}  •  "
            f"<b>OK:</b> {report.ok_files}/{report.total_files}  •  "
            f"<b>Corrupted:</b> {report.corrupt_files}"
        )
        self.table.setRowCount(0)
        for rec in report.records:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(rec.status))
            self.table.setItem(r, 1, QTableWidgetItem(rec.filename))
            self.table.setItem(r, 2, QTableWidgetItem(format_size(rec.size)))
            self.table.setItem(r, 3, QTableWidgetItem(rec.crc))
            self.table.setItem(r, 4, QTableWidgetItem(str(rec.offset)))
            self.table.setItem(r, 5, QTableWidgetItem("100%" if rec.status == "OK" else "DAMAGED"))


class ExtractionDiagnosticDialog(QDialog):
    def __init__(self, parent=None, archive_path="", dest_dir="", error_message=""):
        super().__init__(parent)
        self.setWindowTitle("Extraction Diagnostic")
        self.resize(560, 360)
        self.archive_path = archive_path
        self.error_items = []

        for line in error_message.splitlines():
            line = line.strip()
            m = re.search(r"ERROR:\s*([^:]+)\s*:\s*(.+)$", line)
            if m:
                self.error_items.append({
                    "type": m.group(1).strip(),
                    "file": m.group(2).strip(),
                })

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.table = QTableWidget(len(self.error_items), 2)
        self.table.setHorizontalHeaderLabels(["Damaged File", "Error Reason"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for i, item in enumerate(self.error_items):
            self.table.setItem(i, 0, QTableWidgetItem(item["file"]))
            self.table.setItem(i, 1, QTableWidgetItem(item["type"]))
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_repair = QPushButton("Launch Repair Wizard...")
        btn_repair.setProperty("variant", "primary")
        btn_repair.clicked.connect(self._open_repair)
        btn_row.addWidget(btn_repair)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _open_repair(self):
        from .dialog_repair import ArchiveRepairDialog
        ArchiveRepairDialog(self, initial_archive=self.archive_path).exec()


class ArchiveSanitizerDialog(QDialog):
    def __init__(self, parent=None, archive_path=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Sanitizer & Anti-Mess Optimizer")
        self.resize(640, 420)
        self.sanitizer = ArchiveSanitizer()
        self._last_junk_paths = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        arc_row = QHBoxLayout()
        self.arc_input = QLineEdit(archive_path)
        self.arc_input.setPlaceholderText("Select archive to sanitize...")
        arc_row.addWidget(self.arc_input, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        arc_row.addWidget(btn_browse)

        btn_scan = QPushButton("Analyze")
        btn_scan.clicked.connect(self._analyze)
        arc_row.addWidget(btn_scan)
        layout.addLayout(arc_row)

        self.lbl_summary = QLabel("Analyze an archive to detect OS clutter, dev caches, and nested folders.")
        layout.addWidget(self.lbl_summary)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Action", "Filename", "Category", "Size", "Waste %"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

        btn_box = QHBoxLayout()
        self.btn_purge = QPushButton("Clean & Purge Junk")
        self.btn_purge.setProperty("variant", "danger")
        self.btn_purge.clicked.connect(self._purge_junk)

        self.btn_smart_extract = QPushButton("Smart Extract (Sanitized)")
        self.btn_smart_extract.setProperty("variant", "primary")
        self.btn_smart_extract.clicked.connect(self._smart_extract)

        btn_box.addWidget(self.btn_purge)
        btn_box.addWidget(self.btn_smart_extract)
        btn_box.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)

        if archive_path and os.path.isfile(archive_path):
            self._analyze()

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Archive", "", "Archives (*.zip *.7z *.rar *.tar);;All Files (*.*)")
        if fp:
            self.arc_input.setText(fp)
            self._analyze()

    def _analyze(self):
        arc = self.arc_input.text().strip()
        if not os.path.isfile(arc):
            return
        report = self.sanitizer.analyze(arc)
        total_bytes = max(1, report.total_size)
        self.lbl_summary.setText(
            f"<b>Total Files:</b> {report.total_files}  •  "
            f"<b>Junk Items:</b> {len(report.junk_items)} ({format_size(report.junk_size)})  •  "
            f"<b>Double-Nesting:</b> {'Yes' if report.has_double_nesting else 'No'}"
        )
        self.table.setRowCount(0)
        self._last_junk_paths = []
        for j in report.junk_items:
            self._last_junk_paths.append(j.path)
            r = self.table.rowCount()
            self.table.insertRow(r)
            pct = (j.size / total_bytes) * 100.0
            self.table.setItem(r, 0, QTableWidgetItem("PURGE"))
            self.table.setItem(r, 1, QTableWidgetItem(j.path))
            self.table.setItem(r, 2, QTableWidgetItem(j.category))
            self.table.setItem(r, 3, QTableWidgetItem(format_size(j.size)))
            self.table.setItem(r, 4, QTableWidgetItem(f"{pct:.1f}%"))

    def _purge_junk(self):
        arc = self.arc_input.text().strip()
        if not os.path.isfile(arc):
            return
        base, ext = os.path.splitext(arc)
        out = f"{base}_sanitized{ext or '.zip'}"
        ok, msg, _ = self.sanitizer.create_sanitized_archive(arc, out, self._last_junk_paths)
        QMessageBox.information(self, "Sanitizer", msg) if ok else QMessageBox.warning(self, "Sanitizer", msg)

    def _smart_extract(self):
        arc = self.arc_input.text().strip()
        if not os.path.isfile(arc):
            return
        dest = QFileDialog.getExistingDirectory(self, "Select Smart Extract Destination", os.path.dirname(arc))
        if not dest:
            return
        ok, msg, _ = self.sanitizer.smart_extract(arc, dest)
        QMessageBox.information(self, "Smart Extract", msg) if ok else QMessageBox.warning(self, "Smart Extract", msg)
