"""
Visual storage breakdown Donut Chart & table dialog.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QWidget, QLabel, QPushButton, QAbstractItemView
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF
from ..core.utils import format_size

_CHART_PALETTE = [
    "#3b82f6", "#06b6d4", "#10b981", "#f59e0b",
    "#ec4899", "#8b5cf6", "#f97316", "#64748b",
]


class DonutChartWidget(QWidget):
    """Custom QPainter antialiased donut chart with center total readout."""

    def __init__(self, slices=None, total_bytes=0, parent=None):
        super().__init__(parent)
        self.slices = slices or []
        self.total_bytes = total_bytes
        self.setMinimumSize(220, 220)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height()) - 28
        if side <= 20:
            return
        chart_rect = QRectF(
            (rect.width() - side) / 2.0,
            (rect.height() - side) / 2.0,
            side,
            side,
        )

        if self.total_bytes <= 0 or not self.slices:
            pen = QPen(QColor("#334155"), 22, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.drawEllipse(chart_rect)
        else:
            start_angle = 90 * 16
            for idx, sl in enumerate(self.slices):
                val = sl["size"]
                if val <= 0:
                    continue
                span = -int(round((val / self.total_bytes) * 360 * 16))
                if span == 0:
                    span = -16
                color = QColor(_CHART_PALETTE[idx % len(_CHART_PALETTE)])
                pen = QPen(color, 24, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
                painter.setPen(pen)
                painter.drawArc(chart_rect, start_angle, span)
                start_angle += span

        # Center total label
        painter.setPen(QColor("#94a3b8"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(chart_rect.adjusted(0, -18, 0, 0), Qt.AlignmentFlag.AlignCenter, "Total Size")

        painter.setPen(QColor("#f1f5f9"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(chart_rect.adjusted(0, 14, 0, 0), Qt.AlignmentFlag.AlignCenter, format_size(self.total_bytes))
        painter.end()


class StorageChartDialog(QDialog):
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        self.setWindowTitle("Storage Breakdown Chart")
        self.resize(680, 400)
        self.items = sorted(items or [], key=lambda x: x.get("size", 0), reverse=True)
        total_size = sum(max(0, int(i.get("size", 0))) for i in self.items)

        # Top 7 + Other for clean donut slices
        slices = list(self.items[:7])
        if len(self.items) > 7:
            other_sz = sum(max(0, int(i.get("size", 0))) for i in self.items[7:])
            slices.append({"name": f"Other ({len(self.items) - 7} items)", "size": other_sz})

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        body = QHBoxLayout()
        body.setSpacing(16)

        self.chart = DonutChartWidget(slices=slices, total_bytes=total_size, parent=self)
        body.addWidget(self.chart, 0)

        self.table = QTableWidget(len(self.items), 3)
        self.table.setHorizontalHeaderLabels(["Name / Category", "Size", "Share"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        for i, item in enumerate(self.items):
            sz = max(0, int(item.get("size", 0)))
            pct = (sz / total_size * 100.0) if total_size > 0 else 0.0
            self.table.setItem(i, 0, QTableWidgetItem(str(item.get("name", ""))))
            sz_item = QTableWidgetItem(format_size(sz))
            sz_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 1, sz_item)
            pct_item = QTableWidgetItem(f"{pct:.1f}%")
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 2, pct_item)

        body.addWidget(self.table, 1)
        layout.addLayout(body, 1)

        footer = QHBoxLayout()
        footer.addWidget(QLabel(f"{len(self.items)} item(s) analyzed"))
        footer.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)
