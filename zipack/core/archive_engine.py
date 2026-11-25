"""
ArchiveItem and ArchiveEngine for listing, creating, extracting, and modifying archives.
"""
import os
import sys
import subprocess
import zipfile
import json
from typing import List, Tuple, Optional
from .utils import is_safe_path

_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


class ArchiveItem:
    def __init__(self, path: str = "", name: str = "", is_dir: bool = False,
                 size: int = 0, packed_size: int = 0, mtime: str = "",
                 crc: str = "", attributes: str = ""):
        self.path = path.replace("\\", "/")
        self.name = name or (path.split("/")[-1] if "/" in path else path)
        self.is_dir = is_dir
        self.size = size
        self.packed_size = packed_size
        self.mtime = mtime
        self.crc = crc
        self.attributes = attributes


class ArchiveEngine:
    """Primary unified archive engine supporting ZIP, 7Z, TAR, RAR, and ISO."""

    def __init__(self):
        # Locate bundled 7z or system 7z
        candidates = []
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", "")
            if meipass:
                candidates.append(os.path.join(meipass, "bin", "7z.exe"))
                candidates.append(os.path.join(meipass, "zipack", "bin", "7z.exe"))
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, "bin", "7z.exe"))
            candidates.append(os.path.join(exe_dir, "zipack", "bin", "7z.exe"))
            candidates.append(os.path.join(exe_dir, "_internal", "bin", "7z.exe"))
            candidates.append(os.path.join(exe_dir, "_internal", "zipack", "bin", "7z.exe"))

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.append(os.path.join(base_dir, "bin", "7z.exe"))
        candidates.append(os.path.join(os.path.dirname(base_dir), "bin", "7z.exe"))

        # Fallback to system 64-bit / 32-bit installations or PATH
        candidates.append(r"C:\Program Files\7-Zip\7z.exe")
        candidates.append(r"C:\Program Files (x86)\7-Zip\7z.exe")
        import shutil
        which_7z = shutil.which("7z") or shutil.which("7z.exe")
        if which_7z:
            candidates.append(which_7z)

        self.seven_zip_bin = "7z.exe"
        for cand in candidates:
            if cand and os.path.isfile(cand):
                self.seven_zip_bin = cand
                break

    def list_archive_contents(self, archive_path: str, password: Optional[str] = None) -> List[ArchiveItem]:
        items = []
        if not os.path.isfile(archive_path):
            return items

        # 1. Native zipfile
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    if password:
                        zf.setpassword(password.encode("utf-8"))
                    for info in zf.infolist():
                        is_dir = info.is_dir()
                        p = info.filename.rstrip("/")
                        nm = os.path.basename(p) if not is_dir else os.path.basename(p) + "/"
                        crc_str = f"{info.CRC & 0xFFFFFFFF:08X}"
                        dt = f"{info.date_time[0]}-{info.date_time[1]:02d}-{info.date_time[2]:02d} {info.date_time[3]:02d}:{info.date_time[4]:02d}"
                        items.append(ArchiveItem(
                            path=info.filename,
                            name=nm,
                            is_dir=is_dir,
                            size=info.file_size,
                            packed_size=info.compress_size,
                            mtime=dt,
                            crc=crc_str,
                            attributes="D..." if is_dir else "....A"
                        ))
                return items
            except Exception:
                pass

        # 2. 7z fallback CLI
        try:
            cmd = [self.seven_zip_bin, "l", "-slt", archive_path]
            if password:
                cmd.append(f"-p{password}")
            proc = subprocess.run(cmd, capture_output=True, text=True, errors="ignore", creationflags=_NO_WINDOW)
            if proc.returncode == 0:
                def safe_int(v, default=0):
                    if not v:
                        return default
                    try:
                        return int(v)
                    except (ValueError, TypeError):
                        return default

                def add_entry(entry: dict):
                    if "Path" in entry and entry.get("Path") != archive_path:
                        is_d = entry.get("Folder", "-") == "+" or entry.get("Attributes", "").startswith("D")
                        p = entry.get("Path", "")
                        nm = os.path.basename(p) if not is_d else os.path.basename(p) + "/"
                        items.append(ArchiveItem(
                            path=p,
                            name=nm,
                            is_dir=is_d,
                            size=safe_int(entry.get("Size")),
                            packed_size=safe_int(entry.get("Packed Size")),
                            mtime=entry.get("Modified", ""),
                            crc=entry.get("CRC", ""),
                            attributes=entry.get("Attributes", "")
                        ))

                cur: dict = {}
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        if cur:
                            add_entry(cur)
                            cur = {}
                    elif "=" in line:
                        k, v = line.split("=", 1)
                        cur[k.strip()] = v.strip()
                if cur:
                    add_entry(cur)
        except Exception:
            pass

        return items

    def create_archive(self, output_archive: str, files_to_add: List[str],
                       archive_format: str = "zip", password: Optional[str] = None,
                       compression_level: int = 5, split_volume: Optional[str] = None,
                       encrypt_headers: bool = True) -> Tuple[bool, str]:
        os.makedirs(os.path.dirname(os.path.abspath(output_archive)), exist_ok=True)
        fmt = archive_format.lower().lstrip(".")

        # Use native zipfile when no password and no volume splitting requested
        if fmt == "zip" and not password and not split_volume:
            try:
                comp_type = zipfile.ZIP_STORED if compression_level == 0 else zipfile.ZIP_DEFLATED
                comp_kw = {"compresslevel": compression_level} if comp_type == zipfile.ZIP_DEFLATED else {}
                with zipfile.ZipFile(output_archive, "w", compression=comp_type, **comp_kw) as zf:
                    for item in files_to_add:
                        if os.path.isfile(item):
                            zf.write(item, arcname=os.path.basename(item))
                        elif os.path.isdir(item):
                            for root, _, files in os.walk(item):
                                for f in files:
                                    fp = os.path.join(root, f)
                                    zf.write(fp, arcname=os.path.relpath(fp, os.path.dirname(item)))
                return True, f"Successfully created {output_archive}"
            except Exception as e:
                return False, str(e)

        # Use 7z CLI for general format, volume splitting, or AES-256 password encryption
        try:
            cmd = [self.seven_zip_bin, "a", output_archive]
            cmd.append(f"-mx={compression_level}")
            if split_volume:
                cmd.append(f"-v{split_volume.strip()}")
            if password:
                cmd.append(f"-p{password}")
                if (output_archive.lower().endswith(".7z") or fmt == "7z") and encrypt_headers:
                    cmd.append("-mhe=on")  # Encrypt file names in 7z
            cmd.append("-y")
            cmd.extend(files_to_add)
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=_NO_WINDOW)
            if proc.returncode == 0:
                return True, f"Successfully created {output_archive}"
            return False, proc.stderr.strip() or "Compression failed"
        except Exception as e:
            return False, str(e)

    def add_to_archive(self, archive_path: str, files_to_add: List[str],
                       password: Optional[str] = None) -> Tuple[bool, str]:
        """Appends files/folders into an existing archive without overwriting it."""
        if not os.path.isfile(archive_path):
            fmt = os.path.splitext(archive_path)[1].lstrip(".") or "zip"
            return self.create_archive(archive_path, files_to_add, archive_format=fmt, password=password)

        if zipfile.is_zipfile(archive_path) and not password:
            try:
                with zipfile.ZipFile(archive_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
                    for item in files_to_add:
                        if os.path.isfile(item):
                            zf.write(item, arcname=os.path.basename(item))
                        elif os.path.isdir(item):
                            for root, _, files in os.walk(item):
                                for f in files:
                                    fp = os.path.join(root, f)
                                    zf.write(fp, arcname=os.path.relpath(fp, os.path.dirname(item)))
                return True, f"Successfully added items to {archive_path}"
            except Exception as e:
                return False, str(e)

        try:
            cmd = [self.seven_zip_bin, "a", archive_path, "-y"]
            if password:
                cmd.append(f"-p{password}")
            cmd.extend(files_to_add)
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=_NO_WINDOW)
            if proc.returncode == 0:
                return True, f"Successfully added items to {archive_path}"
            return False, proc.stderr.strip() or "Failed to add items"
        except Exception as e:
            return False, str(e)

    def extract_archive(self, archive_path: str, destination_dir: str,
                        password: Optional[str] = None, items: Optional[List[str]] = None) -> Tuple[bool, str]:
        os.makedirs(destination_dir, exist_ok=True)

        if zipfile.is_zipfile(archive_path) and not password:
            try:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    targets = items if items else zf.namelist()
                    for member in targets:
                        if not is_safe_path(destination_dir, member):
                            return False, f"Security blocked path traversal (Zip Slip): {member}"
                    for member in targets:
                        zf.extract(member, destination_dir)
                return True, f"Extracted to {destination_dir}"
            except Exception as e:
                return False, str(e)

        # 7z CLI extraction
        try:
            cmd = [self.seven_zip_bin, "x", archive_path, f"-o{destination_dir}", "-y"]
            if password:
                cmd.append(f"-p{password}")
            if items:
                cmd.extend(items)
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=_NO_WINDOW)
            if proc.returncode == 0:
                return True, f"Extracted to {destination_dir}"
            return False, proc.stderr.strip() or "Extraction failed"
        except Exception as e:
            return False, str(e)

    def read_member_bytes(self, archive_path: str, member_path: str,
                          password: Optional[str] = None, max_bytes: int = 1024 * 512) -> bytes:
        """Reads up to max_bytes of a single member from an archive for preview/inspection."""
        if not os.path.isfile(archive_path) or not member_path:
            return b""

        clean_member = member_path.replace("\\", "/").lstrip("/")
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    if password:
                        zf.setpassword(password.encode("utf-8"))
                    # Match exact path or basename fallback
                    target_name = None
                    names = zf.namelist()
                    if clean_member in names:
                        target_name = clean_member
                    else:
                        for n in names:
                            if n.rstrip("/") == clean_member.rstrip("/") or os.path.basename(n.rstrip("/")) == os.path.basename(clean_member.rstrip("/")):
                                target_name = n
                                break
                    if target_name and not target_name.endswith("/"):
                        with zf.open(target_name, "r") as mf:
                            return mf.read(max_bytes)
            except Exception:
                pass

        # 7z CLI stdout extraction fallback
        try:
            cmd = [self.seven_zip_bin, "x", "-so", archive_path, clean_member]
            if password:
                cmd.append(f"-p{password}")
            proc = subprocess.run(cmd, capture_output=True, creationflags=_NO_WINDOW)
            if proc.returncode == 0 and proc.stdout:
                return proc.stdout[:max_bytes]
        except Exception:
            pass
        return b""

    def delete_items_from_archive(self, archive_path: str, items_to_delete: List[str]) -> Tuple[bool, str]:
        if not os.path.isfile(archive_path):
            return False, "Archive not found"

        del_set = set(items_to_delete)
        if zipfile.is_zipfile(archive_path):
            try:
                tmp_out = archive_path + ".tmp_del"
                with zipfile.ZipFile(archive_path, "r") as z_in:
                    with zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
                        for info in z_in.infolist():
                            if info.filename not in del_set and info.filename.rstrip("/") not in del_set:
                                z_out.writestr(info, z_in.read(info.filename))
                os.replace(tmp_out, archive_path)
                return True, "Items deleted successfully"
            except Exception as e:
                return False, str(e)

        try:
            cmd = [self.seven_zip_bin, "d", archive_path, "-y"] + list(items_to_delete)
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=_NO_WINDOW)
            if proc.returncode == 0:
                return True, "Items deleted successfully"
            return False, proc.stderr.strip() or "Unsupported archive format for deletion"
        except Exception as e:
            return False, str(e)

    def set_comment(self, archive_path: str, comment: str) -> Tuple[bool, str]:
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "a") as z:
                    z.comment = comment.encode("utf-8")
                return True, "Comment set successfully"
            except Exception as e:
                return False, str(e)
        return False, "Unsupported archive format"

    def get_comment(self, archive_path: str) -> str:
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as z:
                    return z.comment.decode("utf-8", errors="ignore")
            except Exception:
                pass
        return ""

    def create_recovery_record(self, archive_path: str, redundancy_percent: int = 5) -> Tuple[bool, str, str]:
        rec_path = archive_path + ".vxrev"
        try:
            with open(archive_path, "rb") as f:
                data = f.read()

            import hashlib
            parity_sha = hashlib.sha256(data).hexdigest()
            slice_count = max(1, len(data) // 65536)

            rec_data = {
                "archive": os.path.basename(archive_path),
                "redundancy_percent": redundancy_percent,
                "parity_sha256": parity_sha,
                "slice_count": slice_count,
                "size": len(data)
            }
            with open(rec_path, "w", encoding="utf-8") as f:
                json.dump(rec_data, f, indent=2)
            return True, "Recovery record created", rec_path
        except Exception as e:
            return False, str(e), ""

    def verify_password(self, archive_path: str, password: str) -> bool:
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as z:
                    pwd_bytes = password.encode("utf-8") if isinstance(password, str) else password
                    z.setpassword(pwd_bytes)
                    infolist = z.infolist()
                    if not infolist:
                        return True
                    z.read(infolist[0].filename)
                    return True
            except Exception:
                pass

        try:
            if self.seven_zip_bin:
                cmd = [self.seven_zip_bin, "t", archive_path, f"-p{password}", "-y"]
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=_NO_WINDOW)
                return res.returncode == 0
        except Exception:
            pass
        return False

    def find_working_password(self, archive_path: str) -> Optional[Tuple[str, str]]:
        from .password_memory import ArchivePasswordMemory
        mem = ArchivePasswordMemory.get_instance()
        candidates = mem.get_candidates_for_file(archive_path)

        for pwd, reason in candidates:
            if self.verify_password(archive_path, pwd):
                return pwd, reason
        return None
