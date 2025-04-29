# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['waldohunt.py'],
    pathex=[],
    binaries=[],
    datas=[('waldo_images', 'waldo_images'), ('maintheme.mp3', '.'), ('gameover.mp3', '.'), ('machineishere.jpg', '.'), ('waldohunter.pt', '.')],
    hiddenimports=['torch', 'torchvision', 'ultralytics', 'numpy'],
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
    name='waldohunt',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='waldohunt',
)
