---
name: pyinstaller-windows
description: >
  Guide til at pakke en Python-app (FastAPI, Scrapy, uvicorn) som Windows
  installer (.exe) med PyInstaller og Inno Setup — inkl. GitHub Actions CI-build.
  Brug denne skill når nogen vil distribuere en Python desktop-app til Windows,
  pakke en FastAPI-server som standalone .exe, lave en Windows-installer uden UAC,
  bygge PyInstaller spec-filer, sætte Inno Setup op, eller bygge Windows-releases
  via GitHub Actions. Indeholder alle kendte faldgruber fra en reel implementation
  med FastAPI + Scrapy + subprocess-mønstret.
---

# Pakke Python-app til Windows med PyInstaller + Inno Setup

## Overblik — hvad der skal til

Fire nye filer + kodeændringer i eksisterende filer:

| Ny fil | Formål |
|---|---|
| `KlinikPortal.spec` | PyInstaller-konfiguration |
| `KlinikPortal.iss` | Inno Setup installer-script |
| `build_windows.ps1` | Lokalt bygge-script (Windows) |
| `.github/workflows/build-windows.yml` | CI på GitHub (bygger gratis på Windows-runner) |
| `backend/src/klinik/static/.gitkeep` | Sikrer static-mappen eksisterer i git |

---

## Kodeændringer i eksisterende filer

### `main.py` — rækkefølgen er kritisk

```python
"""Modul-docstring."""          # 1. Docstring må gerne stå først
from __future__ import annotations  # 2. __future__ SKAL stå her — før al kode

# 3. Scrapy-worker dispatch — SKAL stå før Twisted importeres
import sys as _sys
if "--scrapy-worker" in _sys.argv:
    import os as _os
    from pathlib import Path as _Path
    if getattr(_sys, "frozen", False):
        _os.chdir(_Path(_sys.executable).parent)
    _sys.argv = [_sys.argv[0]] + [a for a in _sys.argv[1:] if a != "--scrapy-worker"]
    from scrapy.cmdline import execute
    execute()
    _sys.exit(0)

# 4. Resten af imports
import errno, logging, multiprocessing, os, socket, sys, threading, time, webbrowser
from pathlib import Path
import uvicorn

# 5. Frozen-setup: chdir + logfil (ingen konsol i frozen = ingen fejlbeskeder uden logfil)
if getattr(sys, "frozen", False):
    _exe_dir = Path(sys.executable).parent
    os.chdir(_exe_dir)
    (_exe_dir / "data").mkdir(exist_ok=True)
    logging.basicConfig(
        filename=str(_exe_dir / "data" / "klinikportal.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

from klinik.app import app      # noqa: E402
from klinik.config import settings  # noqa: E402


def _find_free_port(start: int, max_tries: int = 20) -> int:
    for port in range(start, start + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError as e:
                # EADDRINUSE = port i brug, EACCES = Windows reserveret port (Hyper-V/WSL)
                if e.errno not in (errno.EADDRINUSE, errno.EACCES):
                    raise
    raise OSError(f"Ingen ledig port fundet i {start}–{start + max_tries - 1}")


if __name__ == "__main__":
    multiprocessing.freeze_support()   # KRITISK på Windows med subprocess
    port = _find_free_port(settings.port)
    threading.Thread(target=_open_browser, args=(port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info", log_config=None)
    #                                                                 ^^^^^^^^^^^^^^
    #                           log_config=None forhindrer "Unable to configure formatter" fejl
```

**Hvorfor denne rækkefølge:**
- `from __future__` skal være første kode-statement — Python fejler ellers med SyntaxError
- Scrapy-worker dispatch skal ske *før* Twisted importeres (Twisted installerer en global reactor ved import)
- `multiprocessing.freeze_support()` skal kaldes i `__main__`-blokken — forhindrer at Windows spawner appen igen og igen som subprocess

### `runner.py` — frozen-aware subprocess

```python
import sys
from pathlib import Path

# Frozen: exe-mappen. Dev: projektrod via __file__
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[4]

def start_crawl(url: str, depth: int = 5):
    if getattr(sys, "frozen", False):
        # Frozen: genbrugEXE som Scrapy-interpreter
        cmd = [sys.executable, "--scrapy-worker", "crawl", "site_spider",
               "-a", f"start_url={url}", "-a", f"max_depth={depth}"]
        env = {**os.environ, "SCRAPY_SETTINGS_MODULE": SCRAPY_SETTINGS}
    else:
        cmd = [sys.executable, "-m", "scrapy", "crawl", "site_spider",
               "-a", f"start_url={url}", "-a", f"max_depth={depth}"]
        env = {**os.environ,
               "SCRAPY_SETTINGS_MODULE": SCRAPY_SETTINGS,
               "PYTHONPATH": f"{PROJECT_ROOT}{os.pathsep}{PROJECT_ROOT / 'backend' / 'src'}"}

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,      # KRITISK: GUI-app har ingen stdin-handle
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        # Forhindrer konsol-vindue + løser stdin-problem i noconsole-apps
        **({"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}),
    )
```

**Hvorfor `stdin=DEVNULL`:** En `console=False` PyInstaller-app har `INVALID_HANDLE_VALUE` som stdin. Når `subprocess.Popen` arver denne handle, fejler Windows med WinError → 500 Internal Server Error. `DEVNULL` omgår det.

### `config.py` — stier til bundtede filer

```python
import sys

# Bundtede read-only filer (templates, assets) ligger i sys._MEIPASS når frozen
# (_internal/ i COLLECT-build). CWD/assets/ eksisterer IKKE i det frosne miljø.
if getattr(sys, "frozen", False):
    _ASSETS_DIR: Path = Path(sys._MEIPASS) / "assets"  # type: ignore[attr-defined]
else:
    _ASSETS_DIR = Path("assets")

class Settings(BaseSettings):
    assets_dir: Path = _ASSETS_DIR   # ikke Path("assets") direkte
    db_path: Path = Path("data") / "klinik.db"   # relativ til CWD = exe-mappe ✓
```

**Skelnen:** `data/` (database, config, logs) = skrivbar, relativ til exe via `os.chdir`. `assets/` (templates, statiske filer) = read-only, bundtet i `_internal/`, kræver `sys._MEIPASS`.

---

## `KlinikPortal.spec`

```python
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

a = Analysis(
    ["main.py"],
    pathex=[".", "backend/src"],   # BEGGE — gør klinik.* og scrapy_crawler.* importerbare
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
        *collect_submodules("scrapy"),    # Twisted bruger string-opslag — skal med
        *collect_submodules("twisted"),
        *collect_submodules("pandas"),
        *collect_submodules("scrapy_crawler.src.crawler"),
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.lifespan.on",
        "uvicorn.logging",
        "pydantic_core",
        "pydantic_settings",
        "lxml", "lxml._elementpath",
        "psutil._pswindows",
        "multiprocessing.spawn",
        "multiprocessing.forkserver",
    ],
    ...
)

exe = EXE(...,
    console=False,   # ingen terminal-vindue
    upx=False,       # UPX-komprimering trigger antivirus-alarmer
)
```

---

## `KlinikPortal.iss` — Inno Setup

```ini
[Setup]
DefaultDirName={localappdata}\Programs\{#AppName}   ; ingen UAC
PrivilegesRequired=lowest

[Icons]
; BRUG {userdesktop} og {userprograms} — IKKE {commondesktop}/{group}
; {commondesktop} og {group} = alle brugere = kræver admin = modstrider PrivilegesRequired=lowest
Name: "{userprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{userdesktop}\{#AppName}";  Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Dirs]
Name: "{app}\data"           ; opret data-mappe ved installation
Name: "{app}\data\exports"
```

`WorkingDir: "{app}"` på genveje er vigtigt — appen bruger relative stier fra sin egen mappe.

---

## GitHub Actions — `.github/workflows/build-windows.yml`

```yaml
jobs:
  build:
    runs-on: windows-latest
    permissions:
      contents: write        # PÅKRÆVET for at oprette GitHub Releases

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - uses: astral-sh/setup-uv@v6
        with: { enable-cache: true }
      - uses: actions/setup-node@v4
        with: { node-version: "22", cache: "npm", cache-dependency-path: frontend/package-lock.json }

      - name: Install Inno Setup 6
        run: choco install innosetup --yes --no-progress
        shell: pwsh

      - run: uv sync
      - name: Build frontend
        run: cd frontend && npm ci && npm run build
        shell: pwsh

      - name: Copy dist
        run: |
          if (Test-Path backend\src\klinik\static\dist) {
            Remove-Item backend\src\klinik\static\dist -Recurse -Force
          }
          Copy-Item frontend\dist backend\src\klinik\static\dist -Recurse
        shell: pwsh

      - name: PyInstaller
        # uv run --with undgår at ændre pyproject.toml/uv.lock
        run: uv run --with "pyinstaller>=6.6" pyinstaller KlinikPortal.spec --clean --noconfirm
        shell: pwsh

      - name: Inno Setup
        run: |
          New-Item -ItemType Directory -Force -Path installer | Out-Null
          & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" KlinikPortal.iss
        shell: pwsh

      - uses: actions/upload-artifact@v4.6.2
        with:
          name: KlinikPortal-windows-installer
          path: installer\KlinikPortal-*.exe
          retention-days: 30

      - name: GitHub Release (kun ved tag-push)
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v2
        with:
          files: installer\KlinikPortal-*.exe
          generate_release_notes: true
```

**Repo-indstilling der skal sættes én gang:**
GitHub → repo → Settings → Actions → General → Workflow permissions → **Read and write permissions**

---

## Fejl vi stødte på og deres løsning

| Fejl | Årsag | Løsning |
|---|---|---|
| `SyntaxError: from __future__ imports must occur at the beginning` | Kode (if-blok) stod før `from __future__` | Flyt `from __future__` til linje 2, efter docstring |
| `Unable to configure formatter 'default'` | uvicorn kan ikke finde sin log-formatter i frozen miljø | `uvicorn.run(..., log_config=None)` |
| `WinError 10013` ved port-binding | Windows reserverer porte (Hyper-V/WSL) — `EACCES` kastes | Fang `errno.EACCES` i tillegg til `EADDRINUSE` i port-loop |
| `500 Internal Server Error` på `/api/crawler/start` | `console=False` app har ingen stdin-handle — `Popen` fejler | `stdin=subprocess.DEVNULL` + `creationflags=CREATE_NO_WINDOW` |
| `IPersistFile::Save 0x80070005 Adgang nægtet` | Inno Setup brugte `{commondesktop}` (alle brugere = admin) | Brug `{userdesktop}` og `{userprograms}` i stedet |
| `ValueError: does not appear to be IPv4 or IPv6` | `except AddressValueError` fanger ikke den `ValueError` som `ip_address()` kaster for domænenavne | Brug `except ValueError` (som er superklassen) |
| `403 Resource not accessible by integration` i GitHub Actions | Token mangler skriveadgang til releases | Tilføj `permissions: contents: write` i workflow + sæt Read/write i repo-indstillinger |

---

## Stifinder til logfil på Windows (debug)

Når appen kører frozen og du ikke kan se konsoloutput:

```
%LOCALAPPDATA%\Programs\KlinikPortal\data\klinikportal.log
```

Skriv denne sti direkte i Windows Stifinders adresselinje.

---

## Byg-sekvens lokalt på Windows

```powershell
# Forudsætninger: Python 3.13 + uv, Node.js, Inno Setup 6
.\build_windows.ps1
# → installer\KlinikPortal-0.x.x-setup.exe
```

## Byg via GitHub Actions

```bash
# Manuelt build (artifact tilgængeligt i 30 dage):
# GitHub → Actions → Build Windows Installer → Run workflow

# Release-build med .exe vedhæftet under Releases:
git tag v0.2.0
git push origin v0.2.0
```

Tagget trigger workflowet automatisk. Workflowet bruger workflow-filen **som den så ud på tag-tidspunktet** — tag derfor først efter alle fixes er committed og pushet til main.
