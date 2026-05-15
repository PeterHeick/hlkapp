# -*- mode: python ; coding: utf-8 -*-
# Debug-build: sæt DEBUG_BUILD=1 som miljøvariabel for at bygge med konsol og
# import-tracing. Kør derefter dist/KlinikPortal/KlinikPortal.exe fra en
# PowerShell — ALLE ImportError og PackageNotFoundError vises på én gang.
#
#   $env:DEBUG_BUILD=1; uv run --with pyinstaller pyinstaller KlinikPortal.spec --clean --noconfirm
#
import os
import sys

DEBUG_BUILD = os.environ.get("DEBUG_BUILD") == "1"

# collect_submodules/collect_all kører FØR Analysis() initialiseres, så pathex
# er ikke aktivt endnu. Lokale pakker der ikke er pip-installerede (kun i
# projektmappen) kan Python ikke importere. Fix: tilføj projektroden manuelt.
sys.path.insert(0, os.path.abspath("."))

import importlib.metadata as _imeta
from PyInstaller.utils.hooks import collect_all, copy_metadata

# collect_all() gør ALT i ét kald: datas + binaries + hiddenimports + metadata.
# Brug det for pakker med dynamiske imports, plugins eller C-extensions.
scrapy_d,    scrapy_b,    scrapy_h    = collect_all("scrapy")
twisted_d,   twisted_b,   twisted_h   = collect_all("twisted")
lxml_d,      lxml_b,      lxml_h      = collect_all("lxml")
pandas_d,    pandas_b,    pandas_h    = collect_all("pandas")
certifi_d,   certifi_b,   certifi_h   = collect_all("certifi")
selenium_d,  selenium_b,  selenium_h  = collect_all("selenium")

# Saml metadata (dist-info) for ALLE installerede pakker dynamisk.
# Undgår at manuelt gætte hvilke pakker der kalder importlib.metadata ved runtime.
_all_metadata = []
for _dist in _imeta.distributions():
    _name = _dist.metadata.get("Name")
    if _name:
        try:
            _all_metadata.extend(copy_metadata(_name))
        except Exception:
            pass

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[".", "backend/src"],
    binaries=[
        *scrapy_b,
        *twisted_b,
        *lxml_b,
        *pandas_b,
        *certifi_b,
        *selenium_b,
    ],
    datas=[
        # App-specifikke filer
        ("backend/src/klinik/static/dist", "klinik/static/dist"),
        ("assets/graph_template.html", "assets"),
        ("assets/hierarchy_template.html", "assets"),
        ("scrapy_crawler/scrapy.cfg", "scrapy_crawler"),
        # Pakke-data fra collect_all (inkl. metadata og datafiler)
        *scrapy_d,
        *twisted_d,
        *lxml_d,
        *pandas_d,
        *certifi_d,
        *selenium_d,
        # Metadata (dist-info) for ALLE installerede pakker — dynamisk genereret
        # så vi ikke manuelt skal gætte hvilke pakker kalder importlib.metadata
        # ved runtime. Undgår PackageNotFoundError uanset afhængighedstræet.
        *_all_metadata,
    ],
    hiddenimports=[
        # Fra collect_all — dynamiske imports PyInstaller ikke finder statisk
        *scrapy_h,
        *twisted_h,
        *lxml_h,
        *pandas_h,
        *certifi_h,
        *selenium_h,
        # scrapy_crawler: lokalpakke — collect_all virker ikke for ikke-installerede
        # pakker, så eksplicit liste bruges som sikkerhedsnet
        "scrapy_crawler",
        "scrapy_crawler.src",
        "scrapy_crawler.src.crawler",
        "scrapy_crawler.src.crawler.settings",
        "scrapy_crawler.src.crawler.pipelines",
        "scrapy_crawler.src.crawler.db",
        "scrapy_crawler.src.crawler.spiders",
        "scrapy_crawler.src.crawler.spiders.site_spider",
        # uvicorn — protokol-backends vælges dynamisk ved opstart
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.lifespan.on",
        "uvicorn.logging",
        # pydantic / fastapi
        "pydantic_core",
        "pydantic_settings",
        # psutil — Windows-backend importeres dynamisk
        "psutil._pswindows",
        # pywin32 — bruges af psutil og andre Windows-pakker
        "win32api",
        "win32con",
        "win32gui",
        # multiprocessing — Windows kræver spawn/forkserver
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
    debug="imports" if DEBUG_BUILD else False,   # import-tracing i debug-build
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,       # UPX-komprimering trigger antivirus-alarmer
    console=DEBUG_BUILD,   # konsol til i debug — ser alle fejl på én gang
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
