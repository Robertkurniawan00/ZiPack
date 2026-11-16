# ZiPack

A modern, high-performance archive manager, compression suite, and shell integration for Windows 10 and 11. Built with PyQt6 and native Windows 11 Desktop Window Manager (DWM) hardware-accelerated Mica materials.

---

## Highlights

- **Smart Password Memory & Pattern Auto-Unlock**: Never re-enter passwords for release series. Remembers passwords per-file and recognizes bracket tags (e.g. `[kuyhaa.me]galaxy.rar` and `[kuyhaa.me] milyway.rar`), domain prefixes, and multi-part sets (`.part*.rar`), auto-unlocking subsequent archives in the background (~15ms) alongside instant in-session caching.
- **Interactive Breadcrumb Bar & Quick Path Input**: Fluent Windows 11 style address bar featuring clickable path segment buttons and quick manual editing mode (`Ctrl+L` / click edit).
- **Deep Drag & Drop File Archiving**: Seamlessly drag and drop files and folders anywhere into the window to pack them into fresh archives, drop onto an active archive tab to append items, or drop archives to inspect immediately.
- **Advanced Archive Creation Dialog**: Full control over output formats (`.zip`, `.7z`, `.tar`), 5 compression levels (Store to Ultra), multi-volume splitting presets (10MB, 100MB, 700MB, 4.3GB DVD, custom sizes), and AES-256 password encryption with header obfuscation.
- **Corrupt Archive Integrity Salvager & Auto-Repair Wizard**: Recovers valid files from damaged, partially downloaded, or header-broken archives utilizing Fast Header Alignment and Deep Stream Carving techniques.
- **Dynamic Multi-Theme Engine**: Seamlessly switch between Dark Glass (Fluent Mica), OLED Pure Black, and Fluent Light Glass themes with persistent configuration across restarts.
- **Smart Extraction Target Selection**: Automated intelligent destination resolution directing outputs to the archive's host directory or user Downloads folder rather than hardcoded temporary locations.
- **Universal Format Support**: Full support for `.rar`, `.7z`, `.zip`, `.tar`, `.gz`, `.bz2`, `.xz`, `.iso`, `.cab`, `.wim`, `.jar`, `.apk`, and multi-part split volumes.
- **Windows 11 Native Mica & Dark Mode**: Authentic DWM Mica Alt / Acrylic materials, dark titlebar caption, native rounded window corners, and subtle accent borders via `dwmapi.dll`.
- **Archive Sanitizer & Smart Layout Optimizer**: Automated detection and removal of cross-platform clutter (macOS `__MACOSX`, `.DS_Store`, Windows `Thumbs.db`, `desktop.ini`, development dependencies `node_modules`, `__pycache__`, `.venv`, and duplicate payloads). Includes anti-mess extraction preventing double `Folder/Folder` nesting and loose desktop flooding.
- **Deep In-Archive Grep**: Search plain text, source code, and regular expressions directly inside compressed archives without extraction.
- **Archive Health Checker & Integrity Self-Test**: Validates CRC32 checksums, stream integrity, and header consistency across entire archives with detailed reporting.
- **DoD 5220.22-M Secure File Shredder**: Permanent 3-pass cryptographic wipe with metadata obfuscation.
- **Multi-Volume Splitter & Missing Chunk Relocator**: Splits large files using presets (Discord, Telegram, FAT32) and detects missing volume sequence chunks.
- **Instant LAN File Transfer**: Micro-server with QR code broadcast for downloading archives across local Wi-Fi without cloud dependencies.
- **Standalone SFX Studio**: Compiles archives into self-extracting standalone Windows `.exe` binaries.
- **Full Windows Explorer Integration**: Cascaded submenus with high-resolution vector icons, file associations, and 1-click system shell integration.
- **Zip Slip & Path Traversal Protection**: Secure extraction path validation preventing arbitrary file overwrite attacks.

---

## Architecture Overview

```
ZiPack/
├── zipack/
│   ├── bin/                    # Bundled 64-bit binaries (7z.exe, zipack_accel.dll, ZiPackCLI.exe, etc.)
│   ├── core/                   # Core business logic and compression engines
│   │   ├── native_accel.py     # C++ Native Acceleration ctypes bridge
│   │   ├── archive_engine.py   # Primary unified archive engine (7z CLI + Python fallback)
│   │   ├── sanitizer.py        # Archive Sanitizer & Anti-Mess layout resolver
│   │   ├── health_checker.py   # Archive integrity and CRC32 verification engine
│   │   ├── archive_grep.py     # In-archive regex & text grep engine
│   │   ├── archive_repair.py   # Corrupt archive header reconstruction engine
│   │   ├── batch_processor.py  # Batch multi-archive extraction & compression
│   │   ├── benchmark.py        # Hardware CPU & compression benchmark
│   │   ├── bookmarks.py        # Project pins and location bookmarks manager
│   │   ├── dedup_analyzer.py   # Duplicate payload and storage waste analyzer
│   │   ├── diff_sync.py        # Archive vs. folder delta comparator and sync
│   │   ├── hasher.py           # Cryptographic hash calculator (SHA256, MD5, CRC32)
│   │   ├── iso_mounter.py      # Windows Virtual Disk Service ISO/VHD mounter
│   │   ├── lan_share.py        # Local network HTTP micro-server & QR code generator
│   │   ├── license_manager.py  # Commercial registration manager
│   │   ├── metadata_inspector.py# Deep file metadata & EXIF inspector
│   │   ├── password_memory.py  # Smart release password memory & pattern matching
│   │   ├── password_vault.py   # Encrypted password vault
│   │   ├── sfx_builder.py      # Standalone self-extracting executable compiler
│   │   ├── shell_integration.py# Windows Explorer context menu & file associations
│   │   ├── shredder.py         # DoD 5220.22-M multi-pass secure file shredder
│   │   ├── splitter.py         # Multi-part volume splitter, detector & merger
│   │   ├── steganography.py    # Steganographic archive embedding in images
│   │   ├── threat_scanner.py   # Double extension & decompression bomb scanner
│   │   ├── transcoder.py       # Direct archive-to-archive format converter
│   │   └── utils.py            # Unified formatting, AppData resolution & path security
│   ├── gui/                    # PyQt6 presentation layer & dialogs
│   │   ├── glass_theme.py      # Dark glass styling tokens and QSS stylesheets
│   │   ├── icons.py            # High-DPI resolution-independent vector icon engine
│   │   ├── mica_effect.py      # Native Windows 11 DWM backdrop API wrapper
│   │   ├── main_window.py      # Main multi-tab application window
│   │   ├── tab_page.py         # Archive & directory browser tab
│   │   └── dialog_*.py         # Dedicated modal dialogs
│   └── main.py                 # Application entry point and CLI handler
├── src_native/                 # Multi-language native components (C++, C#, C)
│   ├── cpp/                    # C++ High-Speed Hardware CRC32 & MMF Accelerator (zipack_accel.dll)
│   │   ├── zipack_accel.h
│   │   ├── zipack_accel.cpp
│   │   └── CMakeLists.txt
│   ├── csharp/                 # C# / .NET Standalone Fast CLI Archiver (ZiPackCLI.exe)
│   │   ├── Program.cs
│   │   └── ZiPackCLI.csproj
│   └── c/                      # Pure C Win32 Single-Instance Silent Launcher (ZiPackLauncher.exe)
│       └── launcher.c
├── modules/                    # PowerShell Administration Module
│   └── ZiPack/
│       ├── ZiPack.psd1
│       └── ZiPack.psm1
├── build_native.bat            # 1-Click native compiler for C++, C#, and C
├── dist/                       # Compiled standalone Windows executable distribution
├── test_zipack.py              # Core engine & native integration automated test suite
├── test_gui.py                 # GUI components automated test suite
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── Zipack.spec                 # PyInstaller build specification
```

---

## Requirements

- **Operating System**: Windows 10 (1903+) or Windows 11 (64-bit recommended).
- **Python**: 3.10 or higher.
- **Dependencies**: Listed in `requirements.txt`.

---

## Installation & Running from Source

1. Clone or download the repository:
   ```bash
   git clone https://github.com/Robertkurniawan00/ZiPack.git
   cd ZiPack
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   python zipack/main.py
   ```
   Or double-click `run_zipack.bat`.

---

## Command Line Interface (CLI)

ZiPack supports direct command-line arguments for system context menus and automation:

| Command | Action |
|---|---|
| `ZiPack.exe <path>` | Opens archive or directory in a new browser tab |
| `ZiPack.exe -xs <archive>` | **Smart Extract (Sanitized)**: Auto-resolves nested folders and strips OS ghosts |
| `ZiPack.exe -x <archive>` | Extracts archive contents to current folder |
| `ZiPack.exe -xd <archive>` | Extracts archive contents into a named subfolder |
| `ZiPack.exe -e <archive>` | Opens interactive extraction destination dialog |
| `ZiPack.exe -a <target>` | Opens Add to Archive dialog |
| `ZiPack.exe -az <target>` | 1-Click quick compression to `.zip` |
| `ZiPack.exe -a7 <target>` | 1-Click high compression to `.7z` |
| `ZiPack.exe -sanitize <archive>` | Opens the Archive Sanitizer dialog |

---

## Multi-Language Native Architecture

ZiPack combines the rapid UI capabilities of Python with the raw execution speed and system integration of native compiled languages:

1. **C++ (Native Memory-Mapped Acceleration DLL)**:
   - **File**: `src_native/cpp/zipack_accel.dll`
   - **Capability**: Hardware-accelerated CRC-32 IEEE 802.3 and Adler-32 hash calculation with zero-copy Win32 Memory-Mapped File (`CreateFileMappingW` / `MapViewOfFile`) streaming.
   - **Integration**: Loaded via Python `ctypes` in `zipack.core.native_accel` with pure-Python fallback.

2. **C# (.NET Standalone High-Speed CLI)**:
   - **File**: `src_native/csharp/ZiPackCLI.exe`
   - **Capability**: Lightning-fast archive extraction, creation, and integrity verification running directly on the CLR without Python startup overhead.

3. **C (Win32 Single-Instance Silent Launcher)**:
   - **File**: `src_native/c/ZiPackLauncher.exe`
   - **Capability**: Pure Win32 API launcher (<70 KB). Employs named mutexes (`Local\ZiPack_SingleInstance_Mutex`) to detect running instances and bring existing windows to foreground without console flickering.

4. **PowerShell (Administrative Automation Module)**:
   - **Files**: `modules/ZiPack/ZiPack.psd1`, `modules/ZiPack/ZiPack.psm1`
   - **Cmdlets**: `Compress-ZiPackArchive`, `Expand-ZiPackArchive`, `Test-ZiPackIntegrity`, `Get-ZiPackVersion`.

To recompile all native components in 1-click:
```cmd
build_native.bat
```

---

## Windows Explorer Shell Integration

Register ZiPack as the default archiver and enable Explorer right-click cascading menus:

1. Open **Tools > System Integration & File Associations...** inside ZiPack.
2. Select your desired file extensions and context menu entries.
3. Click **Apply Default Integration**.

Alternatively, run:
```cmd
Apply_Zipack_Integration.bat
```
To remove integration cleanly at any time, run:
```cmd
Remove_System_Integration.bat
```

---

## Building Standalone Executable

To compile a standalone binary (`dist/ZiPack/ZiPack.exe`) with PyInstaller:

```bash
pyinstaller Zipack.spec --noconfirm
```

Then copy required assets into `dist/ZiPack`:
```bash
python -c "import shutil; shutil.copy('zipack.ico', 'dist/ZiPack/zipack.ico'); shutil.copy('zipack.png', 'dist/ZiPack/zipack.png'); shutil.copytree('zipack/bin', 'dist/ZiPack/bin', dirs_exist_ok=True)"
```

---

## Testing

The automated test suite verifies 100% of core engines, security validations, GUI dialogs, and native multi-language integration:

```bash
python -m unittest test_zipack test_gui
```

Expected result:
```
Ran 72 tests in ~3s
OK
```

---

## Security & Privacy

- **Zip Slip Defense**: Path traversal attacks (e.g. `../../evil.exe`) are actively blocked during extraction.
- **Local Configuration**: Passwords and bookmarks are stored in `%APPDATA%\ZiPack` on the local machine and never transmitted externally.
- **DoD Shredder**: Passes 3 random and complement data sweeps before unlinking disk allocation blocks.
- **Decompression Bomb Guard**: Warns before decompressing files with abnormal compression ratios.

---

## License

This project is licensed under the [MIT License](LICENSE).
