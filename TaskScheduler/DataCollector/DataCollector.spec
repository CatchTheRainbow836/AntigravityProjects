# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/workspace/TaskScheduler/DataCollector/src/main.py'],
    pathex=['/workspace/TaskScheduler/DataCollector/src'],
    binaries=[],
    datas=[('/workspace/TaskScheduler/DataCollector/src/schema.json', '.'), ('/workspace/TaskScheduler/DataCollector/src/db_schema.sql', '.')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='DataCollector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
