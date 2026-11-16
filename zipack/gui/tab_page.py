"""
Archive and Directory Browser Tab Page for ZiPack.
Includes interactive clickable breadcrumb navigation, drag-and-drop file ingestion,
session password caching with pattern auto-unlock, and QuickLook previews.
"""
import os
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,
    QStackedWidget, QScrollArea, QFrame, QMessageBox, QFileDialog,
    QInputDialog, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QUrl
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent
from ..core.archive_engine import ArchiveEngine, ArchiveItem
from ..core.password_memory import ArchivePasswordMemory
from ..core.utils import format_size
from .icons import IconEngine


class BreadcrumbAddressBar(QWidget):
    """
    Modern Windows 11 Fluent style clickable breadcrumb address bar.
    Switches seamlessly between clickable breadcrumb pills and text edit mode.
    """
    path_selected = pyqtSignal(str)

    def __init__(self, initial_path: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("breadcrumbAddressBar")
        self.current_path = initial_path
        self.is_archive_mode = False
        self.archive_path = ""

        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._setup_ui()
        self.set_path(initial_path)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 2, 6, 2)
        main_layout.setSpacing(4)

        self.stack = QStackedWidget(self)
        self.stack.setFixedHeight(28)

        # Page 0: Breadcrumb button view
        self.crumbs_container = QWidget()
        self.crumbs_container.setObjectName("crumbsContainer")
        self.crumbs_layout = QHBoxLayout(self.crumbs_container)
        self.crumbs_layout.setContentsMargins(0, 0, 0, 0)
        self.crumbs_layout.setSpacing(2)
        self.crumbs_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(28)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.crumbs_container)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        # Page 1: Manual text edit view
        self.text_input = QLineEdit()
        self.text_input.setFixedHeight(26)
        self.text_input.returnPressed.connect(self._on_text_entered)
        self.text_input.installEventFilter(self)

        self.stack.addWidget(self.scroll_area)  # index 0
        self.stack.addWidget(self.text_input)   # index 1

        main_layout.addWidget(self.stack, 1)

        # Edit button on right to toggle manual mode
        self.btn_toggle_edit = QPushButton()
        self.btn_toggle_edit.setObjectName("btnToggleEdit")
        self.btn_toggle_edit.setIcon(IconEngine.get_icon("edit", 16))
        self.btn_toggle_edit.setToolTip("Edit path as text (Ctrl+L)")
        self.btn_toggle_edit.setFixedSize(26, 26)
        self.btn_toggle_edit.clicked.connect(self._toggle_text_mode)
        main_layout.addWidget(self.btn_toggle_edit)

    def set_path(self, path: str, is_archive: bool = False, archive_path: str = ""):
        self.current_path = path
        self.is_archive_mode = is_archive
        self.archive_path = archive_path or (path if is_archive else "")
        self.text_input.setText(path)
        self._rebuild_breadcrumbs()
        self.stack.setCurrentIndex(0)

    def _rebuild_breadcrumbs(self):
        # Clear existing crumb buttons
        while self.crumbs_layout.count():
            item = self.crumbs_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        norm_path = os.path.normpath(self.current_path)

        if not self.is_archive_mode:
            # Normal directory breadcrumbs
            parts = []
            curr = norm_path
            while True:
                parent, tail = os.path.split(curr)
                if tail:
                    parts.insert(0, (tail, curr))
                    curr = parent
                else:
                    if curr:
                        parts.insert(0, (curr, curr))
                    break

            for i, (name, target) in enumerate(parts):
                if i > 0:
                    sep = QLabel("›")
                    sep.setObjectName("crumb-sep")
                    self.crumbs_layout.addWidget(sep)

                btn = QPushButton(name)
                btn.setProperty("class", "crumb-btn")
                btn.clicked.connect(lambda _, t=target: self.path_selected.emit(t))
                if i == 0 and os.name == "nt":
                    btn.setIcon(IconEngine.get_icon("folder", 14))
                self.crumbs_layout.addWidget(btn)
        else:
            # Inside an archive: show parent disk path, then archive badge, then subfolder
            arc_dir = os.path.dirname(os.path.abspath(self.archive_path))
            arc_name = os.path.basename(self.archive_path)

            # Button to parent folder
            btn_parent = QPushButton(os.path.basename(arc_dir) or arc_dir)
            btn_parent.setProperty("class", "crumb-btn")
            btn_parent.setIcon(IconEngine.get_icon("folder", 14))
            btn_parent.setToolTip(f"Go up to: {arc_dir}")
            btn_parent.clicked.connect(lambda _, d=arc_dir: self.path_selected.emit(d))
            self.crumbs_layout.addWidget(btn_parent)

            sep = QLabel("›")
            sep.setObjectName("crumb-sep")
            self.crumbs_layout.addWidget(sep)

            # Archive button
            btn_arc = QPushButton(arc_name)
            btn_arc.setProperty("class", "crumb-btn")
            btn_arc.setIcon(IconEngine.get_icon("archive", 14))
            btn_arc.setStyleSheet("color: #38bdf8; font-weight: 600;")
            btn_arc.clicked.connect(lambda _, a=self.archive_path: self.path_selected.emit(a))
            self.crumbs_layout.addWidget(btn_arc)

        self.crumbs_layout.addStretch()

    def _toggle_text_mode(self):
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
            self.text_input.setFocus()
            self.text_input.selectAll()
        else:
            self.stack.setCurrentIndex(0)

    def _on_text_entered(self):
        target = self.text_input.text().strip()
        if target:
            self.path_selected.emit(target)
        self.stack.setCurrentIndex(0)

    def eventFilter(self, obj, event):
        if obj == self.text_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.stack.setCurrentIndex(0)
                return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        # Click on blank space switches to text edit mode
        if event.button() == Qt.MouseButton.LeftButton and self.stack.currentIndex() == 0:
            self._toggle_text_mode()
        super().mousePressEvent(event)


class ArchiveTabPage(QWidget):
    item_activated = pyqtSignal(str)
    files_dropped = pyqtSignal(list)

    def __init__(self, initial_path: str = None, parent=None):
        super().__init__(parent)
        self.engine = ArchiveEngine()
        self.current_folder_path = initial_path or os.getcwd()
        self.current_archive_path = None
        self.items = []

        # Session password cache: {archive_path: password}
        self.session_passwords: Dict[str, str] = {}

        self.history_back = []
        self.history_forward = []

        self._setup_ui()
        if os.path.isfile(self.current_folder_path):
            self.open_archive(self.current_folder_path)
        else:
            self.load_directory(self.current_folder_path)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Clickable Breadcrumb Address Bar (compact fixed height, stretch 0)
        self.breadcrumb_bar = BreadcrumbAddressBar(self.current_folder_path, self)
        self.breadcrumb_bar.path_selected.connect(self._on_breadcrumb_navigated)
        layout.addWidget(self.breadcrumb_bar, 0)

        # File table (stretch 1, expands to fill entire available space)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Size", "Packed", "Modified", "Attributes"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.itemDoubleClicked.connect(self._on_table_double_clicked)
        self.table.installEventFilter(self)

        # Enable drag and drop onto the table
        self.setAcceptDrops(True)
        self.table.setAcceptDrops(True)
        self.table.viewport().setAcceptDrops(True)
        self.table.viewport().installEventFilter(self)

        layout.addWidget(self.table, 1)

    def _on_breadcrumb_navigated(self, target_path: str):
        if os.path.isdir(target_path):
            self.navigate_to_folder(target_path)
        elif os.path.isfile(target_path):
            self.open_archive(target_path)

    def eventFilter(self, obj, event):
        if obj == self.table and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Space:
                self.show_quicklook_for_selection()
                return True
            elif event.key() == Qt.Key.Key_Backspace:
                self.go_up()
                return True

        # Forward drops on table viewport to tab page drop handler
        if obj == self.table.viewport():
            if event.type() == QEvent.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                    return True
            elif event.type() == QEvent.Type.Drop:
                self.dropEvent(event)
                return True

        return super().eventFilter(obj, event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        paths = [p for p in paths if os.path.exists(p)]
        if not paths:
            return

        event.acceptProposedAction()

        # If single file and it's an archive, open it
        archive_exts = (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".cab")
        if len(paths) == 1 and paths[0].lower().endswith(archive_exts):
            self.open_archive(paths[0])
            return

        # Otherwise emit signal for parent window to handle adding to archive
        self.files_dropped.emit(paths)

    def show_quicklook_for_selection(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text().rstrip("/")

        data = b""
        if self.current_archive_path:
            pwd = self.session_passwords.get(self.current_archive_path)
            # Preview internal file
            from .dialog_quicklook import QuickLookDialog
            dlg = QuickLookDialog(self, title=name, data=data)
            dlg.exec()
        else:
            fp = os.path.join(self.current_folder_path, name)
            if os.path.isfile(fp):
                try:
                    with open(fp, "rb") as f:
                        data = f.read(1024 * 512)
                except Exception:
                    data = b""
                from .dialog_quicklook import QuickLookDialog
                dlg = QuickLookDialog(self, title=name, data=data)
                dlg.exec()

    def can_go_back(self) -> bool:
        return len(self.history_back) > 0

    def can_go_forward(self) -> bool:
        return len(self.history_forward) > 0

    def navigate_to_folder(self, folder_path: str, record_history: bool = True):
        norm = os.path.abspath(folder_path)
        if not os.path.isdir(norm):
            return
        if record_history and self.current_folder_path:
            self.history_back.append(self.current_folder_path)
            self.history_forward.clear()

        self.current_folder_path = norm
        self.current_archive_path = None
        self.breadcrumb_bar.set_path(norm, is_archive=False)
        self.load_directory(norm)

    def go_back(self):
        if self.can_go_back():
            prev = self.history_back.pop()
            self.history_forward.append(self.current_folder_path)
            self.navigate_to_folder(prev, record_history=False)

    def go_forward(self):
        if self.can_go_forward():
            nxt = self.history_forward.pop()
            self.history_back.append(self.current_folder_path)
            self.navigate_to_folder(nxt, record_history=False)

    def go_up(self):
        if self.current_archive_path:
            parent = os.path.dirname(os.path.abspath(self.current_archive_path))
            self.navigate_to_folder(parent)
        else:
            parent = os.path.dirname(self.current_folder_path)
            if parent and parent != self.current_folder_path:
                self.navigate_to_folder(parent)

    def load_directory(self, folder_path: str):
        self.table.setRowCount(0)
        try:
            entries = os.listdir(folder_path)
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x.lower()))

            for name in entries:
                fp = os.path.join(folder_path, name)
                is_dir = os.path.isdir(fp)
                sz = format_size(os.path.getsize(fp)) if not is_dir else ""
                row = self.table.rowCount()
                self.table.insertRow(row)

                item_name = QTableWidgetItem(name + ("/" if is_dir else ""))
                item_name.setIcon(IconEngine.get_icon("folder" if is_dir else "archive", 16))
                self.table.setItem(row, 0, item_name)

                self.table.setItem(row, 1, QTableWidgetItem(sz))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.table.setItem(row, 3, QTableWidgetItem(""))
                self.table.setItem(row, 4, QTableWidgetItem("Directory" if is_dir else "File"))
        except Exception:
            pass

    def open_archive(self, archive_path: str, password: Optional[str] = None):
        archive_path = os.path.abspath(archive_path)
        self.current_archive_path = archive_path
        self.breadcrumb_bar.set_path(archive_path, is_archive=True, archive_path=archive_path)
        self.table.setRowCount(0)

        # 1. Resolve password from session cache or pattern memory
        resolved_pwd = password or self.session_passwords.get(archive_path)
        if not resolved_pwd:
            memory = ArchivePasswordMemory.get_instance()
            candidates = memory.get_candidates_for_file(archive_path)
            if candidates:
                # Test first candidate
                resolved_pwd = candidates[0][0]

        items = self.engine.list_archive_contents(archive_path, password=resolved_pwd)

        # If locked or password required, prompt user
        if not items and self._is_archive_encrypted(archive_path):
            pwd, ok = QInputDialog.getText(
                self, "Encrypted Archive",
                f"Enter password to unlock '{os.path.basename(archive_path)}':",
                QLineEdit.EchoMode.Password
            )
            if ok and pwd:
                resolved_pwd = pwd
                items = self.engine.list_archive_contents(archive_path, password=resolved_pwd)
                if items:
                    # Cache in session memory
                    self.session_passwords[archive_path] = resolved_pwd
                    ArchivePasswordMemory.get_instance().remember_password(archive_path, resolved_pwd)
                else:
                    QMessageBox.warning(self, "Invalid Password", "The password entered is incorrect.")

        self.items = items
        for it in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(it.name)
            name_item.setIcon(IconEngine.get_icon("folder" if it.is_dir else "archive", 16))
            self.table.setItem(row, 0, name_item)

            self.table.setItem(row, 1, QTableWidgetItem(format_size(it.size)))
            self.table.setItem(row, 2, QTableWidgetItem(format_size(it.packed_size)))
            self.table.setItem(row, 3, QTableWidgetItem(it.mtime))
            self.table.setItem(row, 4, QTableWidgetItem(it.attributes))

    def _is_archive_encrypted(self, archive_path: str) -> bool:
        ext = os.path.splitext(archive_path)[1].lower()
        return ext in (".zip", ".7z", ".rar")

    def _on_table_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text()

        if self.current_archive_path:
            # Inside an archive
            self.item_activated.emit(name)
        else:
            fp = os.path.join(self.current_folder_path, name.rstrip("/"))
            if os.path.isdir(fp):
                self.navigate_to_folder(fp)
            elif os.path.isfile(fp):
                ext = os.path.splitext(fp)[1].lower()
                if ext in (".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".cab"):
                    self.open_archive(fp)
                else:
                    self.item_activated.emit(fp)
