# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# collect_submodules() kører FØR Analysis() initialiseres, så pathex er ikke
# aktivt endnu. scrapy_crawler er ikke installeret som pakke i uv-miljøet, så
# Python kan ikke importere det — collect_submodules returnerer en tom liste.
# Fix: tilføj projektroden til sys.path manuelt her.
sys.path.insert(0, os.path.abspath("."))

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

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
        # Datafiler (plugins, certs, schemas osv.)
        *collect_data_files("scrapy"),
        *collect_data_files("twisted"),
        *collect_data_files("lxml"),
        *collect_data_files("certifi"),
        # dist-info (metadata-mapper) — kræves når pakker kalder
        # importlib.metadata.version() / requires() ved runtime.
        # collect_data_files() bundter IKKE dist-info — copy_metadata() gør.
        *copy_metadata("lxml"),
        *copy_metadata("scrapy"),
        *copy_metadata("twisted"),
        *copy_metadata("certifi"),
        *copy_metadata("pandas"),
        *copy_metadata("pydantic"),
        *copy_metadata("pydantic-settings"),
        *copy_metadata("fastapi"),
        *copy_metadata("uvicorn"),
        *copy_metadata("httpx"),
        *copy_metadata("psutil"),
        *copy_metadata("beautifulsoup4"),
        *copy_metadata("starlette"),
        *copy_metadata("anyio"),
        *copy_metadata("h11"),
        *copy_metadata("httptools"),
        *copy_metadata("click"),
    ],
    hiddenimports=[
        *collect_submodules("scrapy"),
        *collect_submodules("twisted"),
        *collect_submodules("pandas"),
        # Eksplicit liste som sikkerhedsnet — collect_submodules virker kun hvis
        # sys.path-insert ovenfor lykkedes. Begge tilgange skal med.
        *collect_submodules("scrapy_crawler"),
        "scrapy_crawler",
        "scrapy_crawler.src",
        "scrapy_crawler.src.crawler",
        "scrapy_crawler.src.crawler.settings",
        "scrapy_crawler.src.crawler.pipelines",
        "scrapy_crawler.src.crawler.db",
        "scrapy_crawler.src.crawler.spiders",
        "scrapy_crawler.src.crawler.spiders.site_spider",
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
