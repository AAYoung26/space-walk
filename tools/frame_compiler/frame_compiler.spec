# -*- mode: python ; coding: utf-8 -*-
#
# To build:
#   cd tools/frame_compiler
#   python3 -m venv venv && source venv/bin/activate
#   pip install -r requirements.txt
#   pyinstaller frame_compiler.spec
#
# Output: dist/Frame Compiler.app

import imageio_ffmpeg
import os

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

block_cipher = None

a = Analysis(
    ["frame_compiler.py"],
    pathex=[],
    binaries=[],
    datas=[
        (ffmpeg_bin, "imageio_ffmpeg/binaries"),
    ],
    hiddenimports=["imageio_ffmpeg"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Frame Compiler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Frame Compiler",
)

app = BUNDLE(
    coll,
    name="Frame Compiler.app",
    icon=None,
    bundle_identifier="com.framecomplier.app",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": "1.0.0",
    },
)
