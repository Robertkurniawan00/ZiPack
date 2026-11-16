# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

datas = [
    ('zipack.ico', '.'),
    ('zipack.png', '.'),
    ('vxarchive.ico', '.'),
    ('zipack/bin', 'bin'),
    ('zipack/bin', 'zipack/bin')
]
binaries = []
hiddenimports = [
    'zipack',
    'zipack.core',
    'zipack.core.archive_engine',
    'zipack.core.archive_grep',
    'zipack.core.archive_repair',
    'zipack.core.batch_processor',
    'zipack.core.benchmark',
    'zipack.core.bookmarks',
    'zipack.core.dedup_analyzer',
    'zipack.core.diff_sync',
    'zipack.core.hasher',
    'zipack.core.health_checker',
    'zipack.core.iso_mounter',
    'zipack.core.lan_share',
    'zipack.core.license_manager',
    'zipack.core.metadata_inspector',
    'zipack.core.password_memory',
    'zipack.core.password_vault',
    'zipack.core.sanitizer',
    'zipack.core.sfx_builder',
    'zipack.core.shell_integration',
    'zipack.core.shredder',
    'zipack.core.splitter',
    'zipack.core.steganography',
    'zipack.core.threat_scanner',
    'zipack.core.transcoder',
    'zipack.core.utils',
    'zipack.gui',
    'zipack.gui.main_window',
    'zipack.gui.tab_page',
    'zipack.gui.glass_theme',
    'zipack.gui.icons',
    'zipack.gui.mica_effect',
    'zipack.gui.dialog_vault',
    'zipack.gui.dialogs_base',
    'zipack.gui.dialogs_pro',
    'vxarchive',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets'
]

tmp_ret = collect_all('qrcode')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]


a = Analysis(
    ['zipack/main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZiPack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='zipack.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZiPack',
)
