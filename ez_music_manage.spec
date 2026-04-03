# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


hiddenimports = []
hiddenimports += collect_submodules("pyncm")
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("webview")
hiddenimports += ["webview.platforms.cocoa"]

datas = [
    ("frontend", "frontend"),
]


a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=[],
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
    name="EZ Music Manage",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="EZ Music Manage",
)

app = BUNDLE(
    coll,
    name="EZ Music Manage.app",
    icon="assets/icon/emm_app_icon.icns",
    bundle_identifier="com.joeyjo.ezmusicmanage",
)
