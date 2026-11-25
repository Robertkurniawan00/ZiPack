"""
Archive and Directory Browser Tab Page for ZiPack.
Includes interactive clickable breadcrumb navigation, live quick-filter search,
drag-and-drop file ingestion, session password caching with pattern auto-unlock,
context menu actions, and QuickLook previews.
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,
    QStackedWidget, QScrollArea, QFrame, QMessageBox,
    QInputDialog, QLabel, QSizePolicy, QAbstractItemView, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction
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
        while self.crumbs_layout.count():
            item = self.crumbs_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        norm_path = os.path.normpath(self.current_path)

        if not self.is_archive_mode:
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
                    sep.setProperty("class", "crumb-sep")
                    self.crumbs_layout.addWidget(sep)

                btn = QPushButton(name)
                btn.setProperty("class", "crumb-btn")
                btn.clicked.connect(lambda _, t=target: self.path_selected.emit(t))
                if i == 0 and os.name == "nt":
                    btn.setIcon(IconEngine.get_icon("folder", 14))
                self.crumbs_layout.addWidget(btn)
        else:
            arc_dir = os.path.dirname(os.path.abspath(self.archive_path))
            arc_name = os.path.basename(self.archive_path)

            btn_parent = QPushButton(os.path.basename(arc_dir) or arc_dir)
            btn_parent.setProperty("class", "crumb-btn")
            btn_parent.setIcon(IconEngine.get_icon("folder", 14))
            btn_parent.setToolTip(f"Go up to: {arc_dir}")
            btn_parent.clicked.connect(lambda _, d=arc_dir: self.path_selected.emit(d))
            self.crumbs_layout.addWidget(btn_parent)

            sep = QLabel("›")
            sep.setProperty("class", "crumb-sep")
            self.crumbs_layout.addWidget(sep)

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
        if event.button() == Qt.MouseButton.LeftButton and self.stack.currentIndex() == 0:
            self._toggle_text_mode()
        super().mousePressEvent(event)


class ArchiveTabPage(QWidget):
    item_activated = pyqtSignal(str)
    files_dropped = pyqtSignal(list)
    navigation_changed = pyqtSignal(str, bool)  # (title_or_path, is_archive)
    selection_changed = pyqtSignal()

    def __init__(self, initial_path: str = None, parent=None):
        super().__init__(parent)
        self.engine = ArchiveEngine()
        self.current_folder_path = initial_path or os.getcwd()
        self.current_archive_path = None
        self.items: List[ArchiveItem] = []

        # Session password cache: {archive_path: password}
        self.session_passwords: Dict[str, str] = {}

        # History stores tuples of (path, is_archive)
        self.history_back: List[Tuple[str, bool]] = []
        self.history_forward: List[Tuple[str, bool]] = []

        self._setup_ui()
        if os.path.isfile(self.current_folder_path):
            self.open_archive(self.current_folder_path, record_history=False)
        else:
            self.load_directory(self.current_folder_path)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Top navigation + quick-filter row
        nav_row = QHBoxLayout()
        nav_row.setSpacing(6)

        self.breadcrumb_bar = BreadcrumbAddressBar(self.current_folder_path, self)
        self.breadcrumb_bar.path_selected.connect(self._on_breadcrumb_navigated)
        nav_row.addWidget(self.breadcrumb_bar, 1)

        self.filter_input = QLineEdit()
        self.filter_input.setObjectName("filterBar")
        self.filter_input.setPlaceholderText("Filter files...")
        self.filter_input.setClearButtonEnabled(True)
        self.filter_input.setFixedWidth(210)
        self.filter_input.setFixedHeight(34)
        self.filter_input.textChanged.connect(self._apply_filter)
        nav_row.addWidget(self.filter_input, 0)

        layout.addLayout(nav_row, 0)

        # File table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Size", "Packed", "Modified", "Attributes"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.itemDoubleClicked.connect(self._on_table_double_clicked)
        self.table.itemSelectionChanged.connect(lambda: self.selection_changed.emit())
        self.table.installEventFilter(self)

        self.setAcceptDrops(True)
        self.table.setAcceptDrops(True)
        self.table.viewport().setAcceptDrops(True)
        self.table.viewport().installEventFilter(self)

        layout.addWidget(self.table, 1)

    def _apply_filter(self, query: str):
        q = query.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            name = item.text().lower() if item else ""
            self.table.setRowHidden(row, bool(q) and q not in name)

    def _on_breadcrumb_navigated(self, target_path: str):
        if os.path.isdir(target_path):
            self.navigate_to_folder(target_path)
        elif os.path.isfile(target_path):
            self.open_archive(target_path)
        else:
            QMessageBox.warning(self, "Path Not Found", f"The path does not exist:\n{target_path}")

    def eventFilter(self, obj, event):
        if obj == self.table and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Space:
                self.show_quicklook_for_selection()
                return True
            elif event.key() == Qt.Key.Key_Backspace:
                self.go_up()
                return True
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                selected = self.table.selectedItems()
                if selected:
                    self._on_table_double_clicked(selected[0])
                return True

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

        archive_exts = tuple(IconEngine.ARCHIVE_EXTS)
        if len(paths) == 1 and paths[0].lower().endswith(archive_exts):
            self.open_archive(paths[0])
            return

        self.files_dropped.emit(paths)

    def _get_selected_member_bytes(self, name: str) -> Tuple[bytes, str]:
        """Returns (raw_bytes, display_title) for QuickLook / Hash / Metadata."""
        if self.current_archive_path:
            pwd = self.session_passwords.get(self.current_archive_path)
            member_path = name
            for it in self.items:
                if it.name.rstrip("/") == name:
                    member_path = it.path
                    break
            data = self.engine.read_member_bytes(self.current_archive_path, member_path, password=pwd)
            return data, name
        fp = os.path.join(self.current_folder_path, name)
        if os.path.isfile(fp):
            try:
                with open(fp, "rb") as f:
                    return f.read(1024 * 512), name
            except Exception:
                return b"", name
        return b"", name

    def show_quicklook_for_selection(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text().rstrip("/")
        data, title = self._get_selected_member_bytes(name)
        if not self.current_archive_path and os.path.isdir(os.path.join(self.current_folder_path, name)):
            return
        from .dialog_quicklook import QuickLookDialog
        dlg = QuickLookDialog(self, title=title, data=data)
        dlg.exec()

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
        row = item.row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text().rstrip("/")
        main_win = self.window()

        menu = QMenu(self)
        if self.current_archive_path:
            act_ql = QAction("QuickLook Preview (Space)", self)
            act_ql.triggered.connect(self.show_quicklook_for_selection)
            menu.addAction(act_ql)

            if hasattr(main_win, "_action_extract"):
                act_ext = QAction("Extract Selected...", self)
                act_ext.triggered.connect(main_win._action_extract)
                menu.addAction(act_ext)

            menu.addSeparator()

            act_hash = QAction("Inspect Checksums (CRC32 / SHA-256)...", self)
            act_hash.triggered.connect(lambda: self._inspect_selection_hash(name))
            menu.addAction(act_hash)

            act_meta = QAction("Metadata Inspector...", self)
            act_meta.triggered.connect(lambda: self._inspect_selection_metadata(name))
            menu.addAction(act_meta)

            if hasattr(main_win, "_action_delete_selected"):
                menu.addSeparator()
                act_del = QAction("Delete from Archive", self)
                act_del.triggered.connect(main_win._action_delete_selected)
                menu.addAction(act_del)
        else:
            fp = os.path.join(self.current_folder_path, name)
            is_arc = os.path.isfile(fp) and fp.lower().endswith(tuple(IconEngine.ARCHIVE_EXTS))

            act_open = QAction("Open" if not is_arc else "Browse Archive", self)
            act_open.triggered.connect(lambda: self._on_table_double_clicked(name_item))
            menu.addAction(act_open)

            if is_arc and hasattr(main_win, "_action_extract"):
                act_ext = QAction("Extract Archive...", self)
                act_ext.triggered.connect(main_win._action_extract)
                menu.addAction(act_ext)

                act_san = QAction("Sanitize Archive...", self)
                act_san.triggered.connect(lambda: self._open_sanitizer(fp))
                menu.addAction(act_san)

                act_test = QAction("Test Integrity...", self)
                act_test.triggered.connect(lambda: self._open_health(fp))
                menu.addAction(act_test)

            if hasattr(main_win, "_action_add"):
                act_add = QAction("Add to Archive...", self)
                act_add.triggered.connect(main_win._action_add)
                menu.addAction(act_add)

            if os.path.isfile(fp):
                menu.addSeparator()
                act_ql = QAction("QuickLook Preview (Space)", self)
                act_ql.triggered.connect(self.show_quicklook_for_selection)
                menu.addAction(act_ql)

                act_hash = QAction("Checksum / Hash Inspector...", self)
                act_hash.triggered.connect(lambda: self._inspect_selection_hash(name))
                menu.addAction(act_hash)

                act_share = QAction("Share via LAN (QR)...", self)
                act_share.triggered.connect(lambda: self._open_lan_share(fp))
                menu.addAction(act_share)

                act_shred = QAction("Secure Shred (DoD 5220.22-M)...", self)
                act_shred.triggered.connect(lambda: self._open_shredder(fp))
                menu.addAction(act_shred)

            if hasattr(main_win, "_action_delete_selected"):
                menu.addSeparator()
                act_del = QAction("Delete", self)
                act_del.triggered.connect(main_win._action_delete_selected)
                menu.addAction(act_del)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _inspect_selection_hash(self, name: str):
        data, title = self._get_selected_member_bytes(name)
        from .dialog_hash import HashInspectorDialog
        HashInspectorDialog(self, file_path_or_data=data, display_name=title).exec()

    def _inspect_selection_metadata(self, name: str):
        data, title = self._get_selected_member_bytes(name)
        from .dialog_metadata import MetadataInspectorDialog
        MetadataInspectorDialog(self, file_name=title, raw_data=data).exec()

    def _open_sanitizer(self, fp: str):
        from .dialog_sanitizer import ArchiveSanitizerDialog
        ArchiveSanitizerDialog(self, archive_path=fp).exec()

    def _open_health(self, fp: str):
        from .dialog_health import ArchiveHealthDialog
        ArchiveHealthDialog(self, archive_path=fp).exec()

    def _open_lan_share(self, fp: str):
        from .dialog_lan_share import LANShareDialog
        LANShareDialog(self, file_path=fp).exec()

    def _open_shredder(self, fp: str):
        from .dialog_shredder import ShredderDialog
        ShredderDialog(self, initial_files=[fp]).exec()

    def can_go_back(self) -> bool:
        return len(self.history_back) > 0

    def can_go_forward(self) -> bool:
        return len(self.history_forward) > 0

    def _current_location(self) -> Tuple[str, bool]:
        if self.current_archive_path:
            return (self.current_archive_path, True)
        return (self.current_folder_path, False)

    def navigate_to_folder(self, folder_path: str, record_history: bool = True):
        norm = os.path.abspath(folder_path)
        if not os.path.isdir(norm):
            return
        if record_history and (self.current_folder_path or self.current_archive_path):
            self.history_back.append(self._current_location())
            self.history_forward.clear()

        self.current_folder_path = norm
        self.current_archive_path = None
        self.filter_input.clear()
        self.breadcrumb_bar.set_path(norm, is_archive=False)
        self.load_directory(norm)
        self.navigation_changed.emit(norm, False)

    def go_back(self):
        if self.can_go_back():
            prev_path, is_arc = self.history_back.pop()
            self.history_forward.append(self._current_location())
            if is_arc and os.path.isfile(prev_path):
                self.open_archive(prev_path, record_history=False)
            else:
                self.navigate_to_folder(prev_path, record_history=False)

    def go_forward(self):
        if self.can_go_forward():
            nxt_path, is_arc = self.history_forward.pop()
            self.history_back.append(self._current_location())
            if is_arc and os.path.isfile(nxt_path):
                self.open_archive(nxt_path, record_history=False)
            else:
                self.navigate_to_folder(nxt_path, record_history=False)

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
        self.items = []
        try:
            entries = os.listdir(folder_path)
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x.lower()))

            for name in entries:
                fp = os.path.join(folder_path, name)
                is_dir = os.path.isdir(fp)
                try:
                    st = os.stat(fp)
                    raw_size = st.st_size if not is_dir else 0
                    mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                except OSError:
                    raw_size = 0
                    mtime = ""

                sz = format_size(raw_size) if not is_dir else ""
                row = self.table.rowCount()
                self.table.insertRow(row)

                item_name = QTableWidgetItem(name + ("/" if is_dir else ""))
                item_name.setIcon(IconEngine.get_icon_for_filename(name, is_dir=is_dir, size=16))
                self.table.setItem(row, 0, item_name)

                size_item = QTableWidgetItem(sz)
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 1, size_item)

                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.table.setItem(row, 3, QTableWidgetItem(mtime))
                self.table.setItem(row, 4, QTableWidgetItem("Folder" if is_dir else os.path.splitext(name)[1].upper().lstrip(".") or "File"))

                self.items.append(ArchiveItem(path=fp, name=name, is_dir=is_dir, size=raw_size, mtime=mtime))
        except Exception:
            pass
        self.selection_changed.emit()

    def open_archive(self, archive_path: str, password: Optional[str] = None, record_history: bool = True):
        archive_path = os.path.abspath(archive_path)
        if record_history and (self.current_folder_path or self.current_archive_path) and self.current_archive_path != archive_path:
            self.history_back.append(self._current_location())
            self.history_forward.clear()

        self.current_archive_path = archive_path
        self.current_folder_path = os.path.dirname(archive_path)
        self.filter_input.clear()
        self.breadcrumb_bar.set_path(archive_path, is_archive=True, archive_path=archive_path)
        self.table.setRowCount(0)

        resolved_pwd = password or self.session_passwords.get(archive_path)
        if not resolved_pwd:
            found = self.engine.find_working_password(archive_path)
            if found:
                resolved_pwd = found[0]
                self.session_passwords[archive_path] = resolved_pwd

        items = self.engine.list_archive_contents(archive_path, password=resolved_pwd)

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
                    self.session_passwords[archive_path] = resolved_pwd
                    ArchivePasswordMemory.get_instance().remember_password(archive_path, resolved_pwd)
                else:
                    QMessageBox.warning(self, "Invalid Password", "The password entered is incorrect.")

        self.items = items
        for it in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(it.name)
            name_item.setIcon(IconEngine.get_icon_for_filename(it.name, is_dir=it.is_dir, size=16))
            self.table.setItem(row, 0, name_item)

            size_item = QTableWidgetItem(format_size(it.size) if not it.is_dir else "")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 1, size_item)

            packed_item = QTableWidgetItem(format_size(it.packed_size) if not it.is_dir else "")
            packed_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, packed_item)

            self.table.setItem(row, 3, QTableWidgetItem(it.mtime))
            self.table.setItem(row, 4, QTableWidgetItem(it.attributes))

        self.navigation_changed.emit(archive_path, True)
        self.selection_changed.emit()

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
            self.item_activated.emit(name)
        else:
            fp = os.path.join(self.current_folder_path, name.rstrip("/"))
            if os.path.isdir(fp):
                self.navigate_to_folder(fp)
            elif os.path.isfile(fp):
                ext = os.path.splitext(fp)[1].lower()
                if ext in IconEngine.ARCHIVE_EXTS:
                    self.open_archive(fp)
                else:
                    self.item_activated.emit(fp)
