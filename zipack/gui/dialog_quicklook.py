"""
QuickLook instant preview dialog with image, text, and hex dump modes.
"""
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from ..core.utils import format_size


class QuickLookDialog(QDialog):
    _IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico"}

    def __init__(self, parent=None, title="QuickLook", data=b""):
        super().__init__(parent)
        self.setWindowTitle(f"QuickLook - {title}")
        self.resize(620, 440)
        raw = data if isinstance(data, (bytes, bytearray)) else b""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header info bar
        header = QHBoxLayout()
        lbl_title = QLabel(f"<b>{os.path.basename(title)}</b>")
        lbl_title.setStyleSheet("font-size: 14px;")
        header.addWidget(lbl_title, 1)

        ext = os.path.splitext(title)[1].lower()
        pix = QPixmap()
        is_image = ext in self._IMAGE_EXTS and bool(raw) and pix.loadFromData(raw)
        is_binary = not is_image and bool(raw) and (b"\x00" in raw[:4096])

        mode_name = "Image" if is_image else ("Hex Binary" if is_binary else "Text")
        lbl_meta = QLabel(f"{mode_name}  •  {format_size(len(raw))}")
        lbl_meta.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header.addWidget(lbl_meta)
        layout.addLayout(header)

        if is_image:
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scaled = pix.scaled(560, 340, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(scaled)
            layout.addWidget(img_label, 1)
        else:
            self.text_edit = QTextEdit()
            self.text_edit.setReadOnly(True)
            self.text_edit.setFont(QFont("Consolas", 10))
            if not raw:
                self.text_edit.setPlainText("(Empty file or preview unavailable)")
            elif is_binary:
                self.text_edit.setPlainText(self._format_hex_dump(raw[:8192]))
            else:
                self.text_edit.setPlainText(raw.decode("utf-8", errors="replace"))
            layout.addWidget(self.text_edit, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    @staticmethod
    def _format_hex_dump(data: bytes) -> str:
        lines = []
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{offset:08X}  {hex_part:<47}  |{ascii_part}|")
        return "\n".join(lines)
