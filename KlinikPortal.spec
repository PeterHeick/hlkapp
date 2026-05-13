# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[".", "backend/src"],
    binaries=[],
    datas=[
        ("backend/src/klinik/static/dist", "klinik/static/dist"),
        ("assets/graph_template.html", "assets"),
        ("assets/hierarchy_template.html", "assets"),
        ("scrapy_crawler/scrapy.cfg", "scrapy_crawler"),
        *collect_data_files("scrapy"),
        *collect_data_files("twisted"),
        *collect_data_files("lxml"),
        *collect_data_files("certifi"),
    ],
    hiddenimports=[
        *collect_submodules("scrapy"),
        *collect_submodules("twisted"),
        *collect_submodules("pandas"),
        *collect_submodules("scrapy_crawler"),
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.lifespan.on",
        "uvicorn.logging",
        "pydantic_core",
        "pydantic_settings",
        "lxml",
        "lxml._elementpath",
        "psutil._pswindows",
        "win32api",
        "win32con",
        "win32gui",
        "multiprocessing.spawn",
        "multiprocessing.forkserver",
        "pkg_resources.py2_warn",
    ],
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
    name="KlinikPortal",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
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
    upx=False,
    upx_exclude=[],
    name="KlinikPortal",
)
