"""
High-DPI vector icon generator for ZiPack modern dark glass interface.
Renders crisp, antialiased Fluent-style icons for toolbars, menus, and file listings.
"""
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPainterPath, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF


class IconEngine:
    _cache = {}

    @classmethod
    def get_icon(cls, name: str, size: int = 24) -> QIcon:
        key = (name.lower(), size)
        if key in cls._cache:
            return cls._cache[key]

        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        scale = size / 24.0
        painter.scale(scale, scale)

        n = name.lower()

        if n == "back":
            # Left arrow
            pen = QPen(QColor("#94a3b8"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(16, 12, 8, 12)
            painter.drawLine(12, 8, 8, 12)
            painter.drawLine(12, 16, 8, 12)

        elif n == "forward":
            # Right arrow
            pen = QPen(QColor("#94a3b8"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(8, 12, 16, 12)
            painter.drawLine(12, 8, 16, 12)
            painter.drawLine(12, 16, 16, 12)

        elif n == "up":
            # Up arrow
            pen = QPen(QColor("#94a3b8"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(12, 16, 12, 8)
            painter.drawLine(8, 12, 12, 8)
            painter.drawLine(16, 12, 12, 8)

        elif n == "refresh":
            # Circular refresh
            pen = QPen(QColor("#38bdf8"), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(QRectF(5, 5, 14, 14), 45 * 16, 270 * 16)
            painter.drawLine(15, 5, 19, 5)
            painter.drawLine(19, 5, 19, 9)

        elif n == "add":
            # Archive box with green plus
            # Box base
            grad = QLinearGradient(4, 5, 20, 20)
            grad.setColorAt(0, QColor("#1e293b"))
            grad.setColorAt(1, QColor("#0f172a"))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor("#3b82f6"), 1.6))
            painter.drawRoundedRect(QRectF(4, 6, 16, 14), 2.5, 2.5)
            # Belt/zipper line
            painter.setPen(QPen(QColor("#60a5fa"), 1.2, Qt.PenStyle.DashLine))
            painter.drawLine(12, 6, 12, 20)
            # Green plus circle badge
            painter.setBrush(QBrush(QColor("#16a34a")))
            painter.setPen(QPen(QColor("#ffffff"), 1.0))
            painter.drawEllipse(QRectF(13, 11, 9, 9))
            painter.setPen(QPen(QColor("#ffffff"), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(17, 13, 17, 18)
            painter.drawLine(15, 15, 20, 15)

        elif n == "extract":
            # Archive box with orange unpack arrow
            grad = QLinearGradient(4, 5, 20, 20)
            grad.setColorAt(0, QColor("#1e293b"))
            grad.setColorAt(1, QColor("#0f172a"))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor("#f97316"), 1.6))
            painter.drawRoundedRect(QRectF(4, 8, 16, 12), 2.5, 2.5)
            # Orange outgoing arrow
            pen = QPen(QColor("#fb923c"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(12, 14, 12, 3)
            painter.drawLine(8, 7, 12, 3)
            painter.drawLine(16, 7, 12, 3)

        elif n == "test":
            # Integrity check shield
            path = QPainterPath()
            path.moveTo(12, 3)
            path.lineTo(19, 6)
            path.lineTo(19, 13)
            path.quadTo(19, 19, 12, 22)
            path.quadTo(5, 19, 5, 13)
            path.lineTo(5, 6)
            path.closeSubpath()
            grad = QLinearGradient(5, 3, 19, 22)
            grad.setColorAt(0, QColor("#0369a1"))
            grad.setColorAt(1, QColor("#0284c7"))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor("#38bdf8"), 1.5))
            painter.drawPath(path)
            # Checkmark
            pen = QPen(QColor("#ffffff"), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(9, 12, 11, 14)
            painter.drawLine(11, 14, 16, 9)

        elif n in ("view", "quicklook"):
            # Eye preview icon
            pen = QPen(QColor("#a855f7"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            path = QPainterPath()
            path.moveTo(3, 12)
            path.quadTo(12, 4, 21, 12)
            path.quadTo(12, 20, 3, 12)
            painter.drawPath(path)
            painter.setBrush(QBrush(QColor("#c084fc")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(9.5, 9.5, 5, 5))

        elif n == "delete":
            # Trash can
            pen = QPen(QColor("#ef4444"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(5, 7, 19, 7)
            painter.drawLine(9, 4, 15, 4)
            path = QPainterPath()
            path.moveTo(6.5, 7)
            path.lineTo(7.5, 19)
            path.lineTo(16.5, 19)
            path.lineTo(17.5, 7)
            painter.drawPath(path)
            painter.drawLine(10, 10, 10, 16)
            painter.drawLine(14, 10, 14, 16)

        elif n == "repair":
            # Wrench
            pen = QPen(QColor("#eab308"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(6, 18, 14, 10)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(QRectF(11, 4, 9, 9), 30 * 16, 280 * 16)

        elif n == "vault":
            # Lock / Vault
            pen = QPen(QColor("#fbbf24"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(QRectF(7, 3, 10, 10), 0, 180 * 16)
            painter.setBrush(QBrush(QColor("#d97706")))
            painter.drawRoundedRect(QRectF(5, 10, 14, 11), 2.5, 2.5)
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(11, 13, 2, 2))
            painter.setPen(QPen(QColor("#ffffff"), 1.4))
            painter.drawLine(12, 15, 12, 18)

        elif n == "chart":
            # Donut / Pie chart
            pen = QPen(QColor("#06b6d4"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(QRectF(4, 4, 16, 16), 0, 240 * 16)
            pen2 = QPen(QColor("#ec4899"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen2)
            painter.drawArc(QRectF(4, 4, 16, 16), 250 * 16, 90 * 16)

        elif n == "info":
            # Circular info glyph
            pen = QPen(QColor("#6366f1"), 1.8)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(4, 4, 16, 16))
            painter.setPen(QPen(QColor("#a5b4fc"), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(12, 8)
            painter.drawLine(12, 11, 12, 16)

        elif n == "folder":
            # Fluent folder
            path = QPainterPath()
            path.moveTo(3, 7)
            path.lineTo(9, 7)
            path.lineTo(11, 9)
            path.lineTo(21, 9)
            path.lineTo(21, 19)
            path.lineTo(3, 19)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor("#ca8a04")))
            painter.setPen(QPen(QColor("#eab308"), 1.4))
            painter.drawPath(path)

        elif n == "archive":
            # Archive stack
            painter.setBrush(QBrush(QColor("#2563eb")))
            painter.setPen(QPen(QColor("#60a5fa"), 1.2))
            painter.drawRoundedRect(QRectF(4, 5, 16, 4), 1.5, 1.5)
            painter.setBrush(QBrush(QColor("#1d4ed8")))
            painter.drawRoundedRect(QRectF(4, 10, 16, 4), 1.5, 1.5)
            painter.setBrush(QBrush(QColor("#1e40af")))
            painter.drawRoundedRect(QRectF(4, 15, 16, 4), 1.5, 1.5)
            # Buckle
            painter.setBrush(QBrush(QColor("#f59e0b")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(11, 7, 2, 10))

        elif n == "edit":
            # Pencil edit glyph
            pen = QPen(QColor("#94a3b8"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(5, 19, 9, 19)
            painter.drawLine(6, 18, 15, 9)
            painter.drawLine(15, 9, 17, 7)
            painter.drawLine(17, 7, 19, 9)
            painter.drawLine(19, 9, 10, 18)

        elif n == "sanitizer":
            # Sparkle / clean sweep glyph
            pen = QPen(QColor("#10b981"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(12, 3, 12, 21)
            painter.drawLine(3, 12, 21, 12)
            painter.drawLine(6, 6, 18, 18)
            painter.drawLine(18, 6, 6, 18)
            painter.setBrush(QBrush(QColor("#34d399")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(9, 9, 6, 6))

        elif n == "share":
            # Network share nodes
            pen = QPen(QColor("#38bdf8"), 1.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(7, 12, 17, 6)
            painter.drawLine(7, 12, 17, 18)
            painter.setBrush(QBrush(QColor("#0284c7")))
            painter.drawEllipse(QRectF(3.5, 9.5, 5, 5))
            painter.drawEllipse(QRectF(15, 3.5, 5, 5))
            painter.drawEllipse(QRectF(15, 15.5, 5, 5))

        elif n == "search":
            # Magnifying glass
            pen = QPen(QColor("#94a3b8"), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(4, 4, 12, 12))
            painter.drawLine(QPointF(14.5, 14.5), QPointF(20, 20))

        elif n == "image":
            # Image file icon
            painter.setBrush(QBrush(QColor("#1e293b")))
            painter.setPen(QPen(QColor("#a855f7"), 1.5))
            painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2.5, 2.5)
            painter.setBrush(QBrush(QColor("#c084fc")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(6.5, 7, 3, 3))
            path = QPainterPath()
            path.moveTo(4, 18)
            path.lineTo(10, 12)
            path.lineTo(14, 15)
            path.lineTo(17, 11)
            path.lineTo(20, 18)
            path.closeSubpath()
            painter.drawPath(path)

        elif n == "code":
            # Code brackets </>
            pen = QPen(QColor("#22d3ee"), 1.9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(8, 7, 4, 12)
            painter.drawLine(4, 12, 8, 17)
            painter.drawLine(16, 7, 20, 12)
            painter.drawLine(20, 12, 16, 17)
            painter.drawLine(QPointF(13.5, 6), QPointF(10.5, 18))

        elif n == "text":
            # Document with text lines
            path = QPainterPath()
            path.moveTo(5, 3)
            path.lineTo(14, 3)
            path.lineTo(19, 8)
            path.lineTo(19, 21)
            path.lineTo(5, 21)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor("#1e293b")))
            painter.setPen(QPen(QColor("#60a5fa"), 1.4))
            painter.drawPath(path)
            painter.setPen(QPen(QColor("#93c5fd"), 1.3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(8, 11, 16, 11)
            painter.drawLine(QPointF(8, 14.5), QPointF(16, 14.5))
            painter.drawLine(8, 18, 13, 18)

        else:
            # Generic File
            path = QPainterPath()
            path.moveTo(5, 3)
            path.lineTo(14, 3)
            path.lineTo(19, 8)
            path.lineTo(19, 21)
            path.lineTo(5, 21)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor("#334155")))
            painter.setPen(QPen(QColor("#64748b"), 1.4))
            painter.drawPath(path)

        painter.end()
        icon = QIcon(pix)
        cls._cache[key] = icon
        return icon

    ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".cab", ".wim", ".jar", ".apk"}
    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico", ".svg"}
    CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".c", ".cpp", ".h", ".cs", ".java", ".go", ".rs", ".json", ".xml", ".yaml", ".yml", ".html", ".css"}
    TEXT_EXTS = {".txt", ".md", ".log", ".ini", ".cfg", ".csv", ".bat", ".ps1", ".sh"}

    @classmethod
    def get_icon_for_filename(cls, filename: str, is_dir: bool = False, size: int = 16) -> QIcon:
        if is_dir:
            return cls.get_icon("folder", size)
        import os
        ext = os.path.splitext(filename.rstrip("/"))[1].lower()
        if ext in cls.ARCHIVE_EXTS:
            return cls.get_icon("archive", size)
        if ext in cls.IMAGE_EXTS:
            return cls.get_icon("image", size)
        if ext in cls.CODE_EXTS:
            return cls.get_icon("code", size)
        if ext in cls.TEXT_EXTS:
            return cls.get_icon("text", size)
        return cls.get_icon("file", size)
