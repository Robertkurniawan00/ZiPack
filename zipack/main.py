"""
ZiPack main entry point and command-line handler.
"""
import sys
import os

# Ensure project and package roots are always in sys.path
_cur_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_cur_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if _cur_dir not in sys.path:
    sys.path.insert(0, _cur_dir)

try:
    from zipack.core.archive_engine import ArchiveEngine
except ImportError:
    try:
        from core.archive_engine import ArchiveEngine
    except ImportError:
        from .core.archive_engine import ArchiveEngine


def handle_quick_compress(source_path: str, format_ext: str = "zip") -> int:
    """CLI handler for quick single-click compression (-az, -a7)."""
    if not os.path.exists(source_path):
        return 1
    engine = ArchiveEngine()
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    folder = os.path.dirname(os.path.abspath(source_path))
    out_arc = os.path.join(folder, f"{base_name}.{format_ext.lstrip('.')}")
    ok, msg = engine.create_archive(out_arc, [source_path], archive_format=format_ext)
    return 0 if ok else 1


def handle_extract(archive_path: str, into_subfolder: bool = True, destination: str = None) -> int:
    """CLI handler for quick extraction (-x, -xd, -xs)."""
    if not os.path.isfile(archive_path):
        return 1
    engine = ArchiveEngine()
    folder = destination or os.path.dirname(os.path.abspath(archive_path))
    if into_subfolder:
        base_name = os.path.splitext(os.path.basename(archive_path))[0]
        dest_dir = os.path.join(folder, base_name)
    else:
        dest_dir = folder

    ok, msg = engine.extract_archive(archive_path, dest_dir)
    return 0 if ok else 1


def handle_smart_extract(archive_path: str, destination: str = None) -> int:
    """CLI handler for smart sanitized extraction (-xs)."""
    if not os.path.isfile(archive_path):
        return 1
    try:
        from zipack.core.sanitizer import ArchiveSanitizer
    except ImportError:
        from .core.sanitizer import ArchiveSanitizer
    sanitizer = ArchiveSanitizer()
    dest = destination or os.path.dirname(os.path.abspath(archive_path))
    ok, _, _ = sanitizer.smart_extract(archive_path, dest)
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        if arg1 in ("-az", "--zip") and len(sys.argv) > 2:
            sys.exit(handle_quick_compress(sys.argv[2], "zip"))
        elif arg1 in ("-a7", "--7z") and len(sys.argv) > 2:
            sys.exit(handle_quick_compress(sys.argv[2], "7z"))
        elif arg1 in ("-xs", "--smart-extract") and len(sys.argv) > 2:
            sys.exit(handle_smart_extract(sys.argv[2]))
        elif arg1 in ("-xd", "--subfolder") and len(sys.argv) > 2:
            sys.exit(handle_extract(sys.argv[2], into_subfolder=True))
        elif arg1 in ("-x", "--extract") and len(sys.argv) > 2:
            sys.exit(handle_extract(sys.argv[2], into_subfolder=False))

    from PyQt6.QtWidgets import QApplication, QDialog
    try:
        from zipack.gui.main_window import ZiPackMainWindow
    except ImportError:
        try:
            from gui.main_window import ZiPackMainWindow
        except ImportError:
            from .gui.main_window import ZiPackMainWindow

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.setApplicationName("ZiPack")

    from PyQt6.QtGui import QIcon
    icon_candidates = [
        os.path.join(_parent_dir, "zipack.ico"),
        os.path.join(_cur_dir, "zipack.ico"),
        os.path.join(getattr(sys, "_MEIPASS", ""), "zipack.ico") if getattr(sys, "frozen", False) else "",
        os.path.join(os.path.dirname(sys.executable), "zipack.ico") if getattr(sys, "frozen", False) else "",
        "zipack.ico"
    ]
    for ic in icon_candidates:
        if ic and os.path.isfile(ic):
            app.setWindowIcon(QIcon(ic))
            break

    # GUI-mode CLI flags (-e, -a, -sanitize)
    if len(sys.argv) > 2:
        arg1 = sys.argv[1].lower()
        target = sys.argv[2]
        if arg1 == "-e" and os.path.isfile(target):
            from zipack.gui.dialog_extract import ExtractionPathAndOptionsDialog
            dlg = ExtractionPathAndOptionsDialog(None, default_archive=target)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                handle_extract(target, into_subfolder=False, destination=dlg.get_destination_path())
            sys.exit(0)
        elif arg1 == "-a" and os.path.exists(target):
            from zipack.gui.dialog_add import ArchiveNameAndParametersDialog
            dlg = ArchiveNameAndParametersDialog(None, files_to_add=[target])
            if dlg.exec() == QDialog.DialogCode.Accepted:
                engine = ArchiveEngine()
                engine.create_archive(
                    dlg.get_output_path(), dlg.get_files_to_add(),
                    archive_format=dlg.get_format(), password=dlg.get_password(),
                    compression_level=dlg.get_compression_level(),
                    split_volume=dlg.get_split_volume(),
                    encrypt_headers=dlg.should_encrypt_headers()
                )
            sys.exit(0)
        elif arg1 == "-sanitize" and os.path.isfile(target):
            from zipack.gui.dialog_sanitizer import ArchiveSanitizerDialog
            dlg = ArchiveSanitizerDialog(None, archive_path=target)
            dlg.exec()
            sys.exit(0)

    window = ZiPackMainWindow()
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        window.open_path(sys.argv[1])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
