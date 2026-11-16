"""
Native C++ Accelerator bridge for ultra-fast checksums and memory-mapped file integrity verification.
"""
import os
import sys
import ctypes
import zlib
from typing import Tuple, Optional


class NativeAccelerator:
    _dll = None
    _available = False
    _version_str = "Pure Python Fallback"

    @classmethod
    def initialize(cls) -> bool:
        if cls._dll is not None:
            return cls._available

        # Candidate locations for zipack_accel.dll
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates = [
            os.path.join(base_dir, "src_native", "cpp", "zipack_accel.dll"),
            os.path.join(base_dir, "zipack", "bin", "zipack_accel.dll"),
            os.path.join(base_dir, "bin", "zipack_accel.dll"),
            os.path.join(os.path.dirname(sys.executable), "zipack_accel.dll"),
            os.path.join(os.path.dirname(sys.executable), "bin", "zipack_accel.dll"),
        ]

        for path in candidates:
            if os.path.isfile(path):
                try:
                    dll = ctypes.CDLL(path)
                    dll.zipack_native_version.restype = ctypes.c_char_p
                    cls._version_str = dll.zipack_native_version().decode("utf-8")

                    dll.zipack_crc32.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32]
                    dll.zipack_crc32.restype = ctypes.c_uint32

                    dll.zipack_adler32.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
                    dll.zipack_adler32.restype = ctypes.c_uint32

                    dll.zipack_file_checksum.argtypes = [
                        ctypes.c_wchar_p,
                        ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint64)
                    ]
                    dll.zipack_file_checksum.restype = ctypes.c_int

                    cls._dll = dll
                    cls._available = True
                    return True
                except Exception:
                    continue

        cls._available = False
        return False

    @classmethod
    def is_available(cls) -> bool:
        if cls._dll is None:
            cls.initialize()
        return cls._available

    @classmethod
    def get_version(cls) -> str:
        if cls._dll is None:
            cls.initialize()
        return cls._version_str

    @classmethod
    def crc32(cls, data: bytes, seed: int = 0) -> int:
        if cls.is_available() and cls._dll:
            return cls._dll.zipack_crc32(data, len(data), seed)
        return zlib.crc32(data, seed) & 0xFFFFFFFF

    @classmethod
    def file_fast_checksum(cls, file_path: str) -> Tuple[int, int, int]:
        """
        Calculates (crc32, adler32, file_size) using memory-mapped IO.
        Falls back to buffered stream reading if DLL is unavailable.
        """
        if cls.is_available() and cls._dll:
            out_crc = ctypes.c_uint32()
            out_adler = ctypes.c_uint32()
            out_size = ctypes.c_uint64()
            ret = cls._dll.zipack_file_checksum(file_path, ctypes.byref(out_crc), ctypes.byref(out_adler), ctypes.byref(out_size))
            if ret == 0:
                return out_crc.value, out_adler.value, out_size.value

        # Fallback
        crc = 0
        adler = 1
        total_size = 0
        with open(file_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                total_size += len(chunk)
                crc = zlib.crc32(chunk, crc)
                adler = zlib.adler32(chunk, adler)

        return crc & 0xFFFFFFFF, adler & 0xFFFFFFFF, total_size
