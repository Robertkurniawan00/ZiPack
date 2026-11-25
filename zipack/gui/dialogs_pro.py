"""
10 Pro modal dialogs for ZiPack: Shredder, Transcoder, Steganography, DiffSync, Splitter, ThreatScanner, Repair, Bookmarks, Iso, Metadata.
"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QFileDialog, QMessageBox,
    QAbstractItemView, QListWidget
)
from PyQt6.QtCore import Qt
from ..core.archive_engine import ArchiveEngine
from ..core.shredder import SecureShredder
from ..core.transcoder import ArchiveTranscoder
from ..core.steganography import ArchiveSteganography
from ..core.diff_sync import ArchiveDiffSync
from ..core.splitter import VolumeSplitter
from ..core.threat_scanner import ThreatScanner
from ..core.bookmarks import BookmarkManager
from ..core.iso_mounter import IsoMounter
from ..core.metadata_inspector import MetadataInspector
from ..core.utils import format_size
from .dialog_repair import ArchiveRepairDialog


class ShredderDialog(QDialog):
    def __init__(self, parent=None, initial_files=None):
        super().__init__(parent)
        self.setWindowTitle("Secure File Shredder (DoD 5220.22-M)")
        self.resize(520, 340)
        self.files = list(initial_files or [])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Files to permanently destroy (unrecoverable):</b>"))
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["File Path", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("Overwrite Passes:"))
        self.spin_passes = QSpinBox()
        self.spin_passes.setRange(1, 7)
        self.spin_passes.setValue(3)
        opt_row.addWidget(self.spin_passes)
        opt_row.addStretch()
        layout.addLayout(opt_row)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Files...")
        btn_add.clicked.connect(self._add_files)
        btn_row.addWidget(btn_add)

        btn_shred = QPushButton("Shred Permanently")
        btn_shred.setProperty("variant", "danger")
        btn_shred.clicked.connect(self._shred_all)
        btn_row.addWidget(btn_shred)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self._refresh()

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Files to Shred")
        for p in paths:
            if p not in self.files:
                self.files.append(p)
        self._refresh()

    def _refresh(self):
        self.table.setRowCount(0)
        for f in self.files:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(f))
            self.table.setItem(r, 1, QTableWidgetItem("Pending" if os.path.isfile(f) else "Not Found"))

    def _shred_all(self):
        if not self.files:
            return
        ret = QMessageBox.warning(
            self, "Confirm Permanent Shred",
            f"Permanently destroy {len(self.files)} file(s)? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        passes = self.spin_passes.value()
        for r, fp in enumerate(self.files):
            ok, msg = SecureShredder.shred_file(fp, passes=passes)
            self.table.setItem(r, 1, QTableWidgetItem("Shredded" if ok else f"Error: {msg}"))


class TranscoderDialog(QDialog):
    def __init__(self, parent=None, initial_archive=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Format Transcoder")
        self.resize(500, 260)
        self.engine = ArchiveEngine()
        self.transcoder = ArchiveTranscoder(self.engine)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Convert archive directly to another format:</b>"))

        src_row = QHBoxLayout()
        self.src_input = QLineEdit(initial_archive)
        self.src_input.setPlaceholderText("Source archive...")
        src_row.addWidget(self.src_input, 1)
        btn_src = QPushButton("Browse...")
        btn_src.clicked.connect(self._browse_src)
        src_row.addWidget(btn_src)
        layout.addLayout(src_row)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("Target Format:"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["7z", "zip", "tar"])
        fmt_row.addWidget(self.fmt_combo, 1)
        layout.addLayout(fmt_row)

        pwd_row = QHBoxLayout()
        pwd_row.addWidget(QLabel("Password (opt):"))
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self.pwd_input, 1)
        layout.addLayout(pwd_row)

        layout.addStretch()
        btn_row = QHBoxLayout()
        btn_convert = QPushButton("Convert Archive")
        btn_convert.setProperty("variant", "primary")
        btn_convert.clicked.connect(self._convert)
        btn_row.addWidget(btn_convert)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse_src(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Source Archive", "", "Archives (*.zip *.7z *.rar *.tar *.gz);;All Files (*.*)")
        if fp:
            self.src_input.setText(fp)

    def _convert(self):
        src = self.src_input.text().strip()
        if not os.path.isfile(src):
            QMessageBox.warning(self, "Transcoder", "Please select a valid source archive.")
            return
        fmt = self.fmt_combo.currentText()
        out = f"{os.path.splitext(src)[0]}_converted.{fmt}"
        ok, msg = self.transcoder.convert(src, out, target_format=fmt, password=self.pwd_input.text() or None)
        if ok:
            QMessageBox.information(self, "Conversion Complete", msg)
        else:
            QMessageBox.critical(self, "Conversion Failed", msg)


class SteganographyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Steganographic Secret Vault")
        self.resize(520, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Hide or Extract Archive within Carrier Image (PNG/JPG)</b>"))

        img_row = QHBoxLayout()
        self.img_input = QLineEdit()
        self.img_input.setPlaceholderText("Carrier image (.png / .jpg)...")
        img_row.addWidget(self.img_input, 1)
        btn_img = QPushButton("Image...")
        btn_img.clicked.connect(self._browse_img)
        img_row.addWidget(btn_img)
        layout.addLayout(img_row)

        arc_row = QHBoxLayout()
        self.arc_input = QLineEdit()
        self.arc_input.setPlaceholderText("Archive to embed (.zip / .7z)...")
        arc_row.addWidget(self.arc_input, 1)
        btn_arc = QPushButton("Archive...")
        btn_arc.clicked.connect(self._browse_arc)
        arc_row.addWidget(btn_arc)
        layout.addLayout(arc_row)

        layout.addStretch()
        btn_row = QHBoxLayout()
        btn_hide = QPushButton("Embed Archive")
        btn_hide.setProperty("variant", "primary")
        btn_hide.clicked.connect(self._hide)
        btn_row.addWidget(btn_hide)

        btn_extract = QPushButton("Extract Hidden Archive")
        btn_extract.clicked.connect(self._extract)
        btn_row.addWidget(btn_extract)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse_img(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)")
        if fp:
            self.img_input.setText(fp)

    def _browse_arc(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Archive", "", "Archives (*.zip *.7z *.rar);;All Files (*.*)")
        if fp:
            self.arc_input.setText(fp)

    def _hide(self):
        img = self.img_input.text().strip()
        arc = self.arc_input.text().strip()
        if not os.path.isfile(img) or not os.path.isfile(arc):
            QMessageBox.warning(self, "Steganography", "Please select both a carrier image and an archive.")
            return
        base, ext = os.path.splitext(img)
        out = f"{base}_stego{ext}"
        ok, msg = ArchiveSteganography.hide_archive_in_image(img, arc, out)
        QMessageBox.information(self, "Steganography", msg) if ok else QMessageBox.critical(self, "Error", msg)

    def _extract(self):
        img = self.img_input.text().strip()
        if not os.path.isfile(img):
            QMessageBox.warning(self, "Steganography", "Please select a stego image.")
            return
        out = os.path.splitext(img)[0] + "_extracted.zip"
        ok, msg = ArchiveSteganography.extract_hidden_archive(img, out)
        QMessageBox.information(self, "Steganography", msg) if ok else QMessageBox.warning(self, "Not Found", msg)


class DiffSyncDialog(QDialog):
    def __init__(self, parent=None, initial_archive="", initial_folder=""):
        super().__init__(parent)
        self.setWindowTitle("Smart Archive Diff & Sync")
        self.resize(620, 400)
        self.engine = ArchiveEngine()
        self.diff_engine = ArchiveDiffSync(self.engine)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        row_arc = QHBoxLayout()
        self.arc_input = QLineEdit(initial_archive)
        self.arc_input.setPlaceholderText("Archive path...")
        row_arc.addWidget(self.arc_input, 1)
        btn_arc = QPushButton("Archive...")
        btn_arc.clicked.connect(self._browse_arc)
        row_arc.addWidget(btn_arc)
        layout.addLayout(row_arc)

        row_dir = QHBoxLayout()
        self.dir_input = QLineEdit(initial_folder)
        self.dir_input.setPlaceholderText("Folder path...")
        row_dir.addWidget(self.dir_input, 1)
        btn_dir = QPushButton("Folder...")
        btn_dir.clicked.connect(self._browse_dir)
        row_dir.addWidget(btn_dir)
        layout.addLayout(row_dir)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Relative Path", "Status", "Size Delta"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_cmp = QPushButton("Compare Delta")
        btn_cmp.setProperty("variant", "primary")
        btn_cmp.clicked.connect(self._compare)
        btn_row.addWidget(btn_cmp)

        btn_sync = QPushButton("Sync Changes to Archive")
        btn_sync.clicked.connect(self._sync)
        btn_row.addWidget(btn_sync)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse_arc(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Archive", "", "Archives (*.zip *.7z *.tar);;All Files (*.*)")
        if fp:
            self.arc_input.setText(fp)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder", self.dir_input.text())
        if d:
            self.dir_input.setText(d)

    def _compare(self):
        arc, folder = self.arc_input.text().strip(), self.dir_input.text().strip()
        if not os.path.isfile(arc) or not os.path.isdir(folder):
            QMessageBox.warning(self, "Diff Sync", "Select both a valid archive and folder.")
            return
        diffs = self.diff_engine.compare(arc, folder)
        self.table.setRowCount(0)
        for d in diffs:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(d.rel_path))
            self.table.setItem(r, 1, QTableWidgetItem(d.status))
            self.table.setItem(r, 2, QTableWidgetItem(f"{format_size(d.disk_size)} vs {format_size(d.archive_size)}"))

    def _sync(self):
        arc, folder = self.arc_input.text().strip(), self.dir_input.text().strip()
        if not os.path.isfile(arc) or not os.path.isdir(folder):
            return
        ok, msg = self.diff_engine.sync_to_archive(arc, folder)
        QMessageBox.information(self, "Sync", msg) if ok else QMessageBox.warning(self, "Sync", msg)


class VolumeSplitterDialog(QDialog):
    def __init__(self, parent=None, initial_file=""):
        super().__init__(parent)
        self.setWindowTitle("Multi-Volume Splitter & Joiner")
        self.resize(500, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Split large files into chunks or merge parts:</b>"))

        file_row = QHBoxLayout()
        self.file_input = QLineEdit(initial_file)
        self.file_input.setPlaceholderText("Select file to split or .001 part to join...")
        file_row.addWidget(self.file_input, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        file_row.addWidget(btn_browse)
        layout.addLayout(file_row)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Chunk Size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["10 MB (Discord)", "25 MB (Email)", "100 MB", "700 MB (CD)", "2000 MB (Telegram)"])
        size_row.addWidget(self.size_combo, 1)
        layout.addLayout(size_row)

        layout.addStretch()
        btn_row = QHBoxLayout()
        btn_split = QPushButton("Split File")
        btn_split.setProperty("variant", "primary")
        btn_split.clicked.connect(self._split)
        btn_row.addWidget(btn_split)

        btn_join = QPushButton("Join Volumes")
        btn_join.clicked.connect(self._join)
        btn_row.addWidget(btn_join)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select File")
        if fp:
            self.file_input.setText(fp)

    def _split(self):
        fp = self.file_input.text().strip()
        if not os.path.isfile(fp):
            QMessageBox.warning(self, "Splitter", "Please select a valid file.")
            return
        mb_map = [10, 25, 100, 700, 2000]
        chunk_bytes = mb_map[self.size_combo.currentIndex()] * 1024 * 1024
        ok, msg, parts = VolumeSplitter.split_file(fp, os.path.dirname(fp), chunk_size_bytes=chunk_bytes)
        QMessageBox.information(self, "Split Complete", f"{msg}\nCreated {len(parts)} part(s).") if ok else QMessageBox.critical(self, "Error", msg)

    def _join(self):
        fp = self.file_input.text().strip()
        if not os.path.isfile(fp):
            QMessageBox.warning(self, "Joiner", "Please select the first volume part (.001).")
            return
        out = os.path.splitext(fp)[0] + "_merged"
        ok, msg = VolumeSplitter.join_volumes(fp, out)
        QMessageBox.information(self, "Merge Complete", msg) if ok else QMessageBox.critical(self, "Error", msg)


class ThreatScannerDialog(QDialog):
    def __init__(self, parent=None, archive_items=None, archive_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"Threat & Decompression Bomb Scanner - {archive_name}")
        self.resize(580, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        report = ThreatScanner.scan_archive_items(archive_items or [])
        self.lbl_summary = QLabel(
            f"<b>Risk Level:</b> {report.risk_level}  •  "
            f"<b>Findings:</b> {len(report.threats)}"
        )
        layout.addWidget(self.lbl_summary)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Severity / Type", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        if not report.threats:
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem("CLEAN"))
            self.table.setItem(0, 1, QTableWidgetItem("No suspicious double extensions, path traversals, or zip bombs detected."))
        else:
            for t in report.threats:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(t.get("severity", report.risk_level))))
                self.table.setItem(r, 1, QTableWidgetItem(str(t.get("reason", t))))
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)


class BookmarkHubDialog(QDialog):
    def __init__(self, parent=None, current_path=""):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks & Project Pinboard")
        self.resize(480, 340)
        self.current_path = current_path
        self.bm = BookmarkManager.get_instance()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Pinned folders and project hubs:</b>"))
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._open_selected)
        layout.addWidget(self.list_widget, 1)

        btn_row = QHBoxLayout()
        btn_pin = QPushButton("Pin Current Folder")
        btn_pin.setProperty("variant", "primary")
        btn_pin.clicked.connect(self._pin_current)
        btn_row.addWidget(btn_pin)

        btn_open = QPushButton("Open")
        btn_open.clicked.connect(self._open_selected)
        btn_row.addWidget(btn_open)

        btn_del = QPushButton("Remove")
        btn_del.clicked.connect(self._remove_selected)
        btn_row.addWidget(btn_del)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        self._refresh()

    def _refresh(self):
        self.list_widget.clear()
        for item in self.bm.get_all():
            self.list_widget.addItem(f"{item.get('name', '')}  —  {item.get('path', '')}")

    def _pin_current(self):
        if self.current_path:
            name = os.path.basename(self.current_path) or self.current_path
            self.bm.add_bookmark(name, self.current_path)
            self._refresh()

    def _remove_selected(self):
        row = self.list_widget.currentRow()
        items = self.bm.get_all()
        if 0 <= row < len(items):
            self.bm.remove_bookmark(items[row]["path"])
            self._refresh()

    def _open_selected(self):
        row = self.list_widget.currentRow()
        items = self.bm.get_all()
        if 0 <= row < len(items):
            target = items[row]["path"]
            p = self.parent()
            if p and hasattr(p, "open_path"):
                p.open_path(target)
                self.accept()


class IsoMounterDialog(QDialog):
    def __init__(self, parent=None, initial_iso=""):
        super().__init__(parent)
        self.setWindowTitle("Virtual Disk / ISO Mounter")
        self.resize(460, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Mount ISO or VHD as Windows virtual drive:</b>"))

        row = QHBoxLayout()
        self.iso_input = QLineEdit(initial_iso)
        self.iso_input.setPlaceholderText("Select .iso or .vhd image...")
        row.addWidget(self.iso_input, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)
        layout.addLayout(row)

        layout.addStretch()
        btn_row = QHBoxLayout()
        btn_mount = QPushButton("Mount")
        btn_mount.setProperty("variant", "primary")
        btn_mount.clicked.connect(self._mount)
        btn_row.addWidget(btn_mount)

        btn_dismount = QPushButton("Dismount")
        btn_dismount.clicked.connect(self._dismount)
        btn_row.addWidget(btn_dismount)

        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Disk Image", "", "Disk Images (*.iso *.vhd *.vhdx);;All Files (*.*)")
        if fp:
            self.iso_input.setText(fp)

    def _mount(self):
        ok, msg = IsoMounter.mount_image(self.iso_input.text().strip())
        QMessageBox.information(self, "ISO Mounter", msg) if ok else QMessageBox.warning(self, "ISO Mounter", msg)

    def _dismount(self):
        ok, msg = IsoMounter.dismount_image(self.iso_input.text().strip())
        QMessageBox.information(self, "ISO Mounter", msg) if ok else QMessageBox.warning(self, "ISO Mounter", msg)


class MetadataInspectorDialog(QDialog):
    def __init__(self, parent=None, file_name="", raw_data=b""):
        super().__init__(parent)
        self.setWindowTitle(f"Metadata Inspector - {file_name}")
        self.resize(500, 340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        meta = MetadataInspector.inspect(file_name, raw_data if isinstance(raw_data, (bytes, bytearray)) else b"")
        self.table = QTableWidget(len(meta), 2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        for i, (k, v) in enumerate(meta.items()):
            self.table.setItem(i, 0, QTableWidgetItem(str(k)))
            self.table.setItem(i, 1, QTableWidgetItem(str(v)))
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
