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
        # Scrapy 2.15+ kalder inspect.getsource() på hvert callback for at
        # opdage forældet generator-brug. I frozen app findes .py-filer ikke
        # (kun bytecode) — getsource() kaster OSError og Scrapy dropper hele
        # responsen lydløst. Resultat: 0 sider crawlet, ingen fejlbesked.
        import scrapy.utils.misc as _scrapy_misc
        _orig_is_gen = _scrapy_misc.is_generator_with_return_value
        def _safe_is_generator(func):  # type: ignore[no-untyped-def]
            try:
                return _orig_is_gen(func)
            except OSError:
                return False
        _scrapy_misc.is_generator_with_return_value = _safe_is_generator
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
import os, sys

# collect_submodules() kører FØR Analysis() — pathex er ikke aktivt endnu.
# Lokale pakker der ikke er pip-installerede (kun i projektmappen) kan Python
# derfor ikke importere, og collect_submodules returnerer en tom liste.
# Fix: tilføj projektroden manuelt til sys.path her i toppen af spec-filen.
sys.path.insert(0, os.path.abspath("."))

import importlib.metadata as _imeta
from PyInstaller.utils.hooks import collect_all, copy_metadata

# collect_all() er den rigtige løsning — ét kald håndterer datas + binaries +
# hiddenimports + metadata. Brug det for pakker med C-extensions, plugins
# eller dynamiske imports. Erstatter collect_data_files + collect_submodules +
# copy_metadata i separate kald.
scrapy_d,  scrapy_b,  scrapy_h  = collect_all("scrapy")
twisted_d, twisted_b, twisted_h = collect_all("twisted")
lxml_d,    lxml_b,    lxml_h    = collect_all("lxml")
pandas_d,  pandas_b,  pandas_h  = collect_all("pandas")
certifi_d, certifi_b, certifi_h = collect_all("certifi")

# Saml metadata (dist-info) for ALLE installerede pakker dynamisk.
# Undgår at manuelt vedligeholde en liste — enhver pakke der kalder
# importlib.metadata.version() ved runtime vil finde sin dist-info.
_all_metadata = []
for _dist in _imeta.distributions():
    _name = _dist.metadata.get("Name")
    if _name:
        try:
            _all_metadata.extend(copy_metadata(_name))
        except Exception:
            pass

a = Analysis(
    ["main.py"],
    pathex=[".", "backend/src"],
    binaries=[*scrapy_b, *twisted_b, *lxml_b, *pandas_b, *certifi_b],
    datas=[
        ("backend/src/klinik/static/dist", "klinik/static/dist"),
        ("assets/graph_template.html", "assets"),
        ("assets/hierarchy_template.html", "assets"),
        ("scrapy_crawler/scrapy.cfg", "scrapy_crawler"),
        *scrapy_d, *twisted_d, *lxml_d, *pandas_d, *certifi_d,
        # Metadata for alle installerede pakker — aldrig manuelt gætte listen
        *_all_metadata,
    ],
    hiddenimports=[
        *scrapy_h, *twisted_h, *lxml_h, *pandas_h, *certifi_h,
        # Lokalpakke — eksplicit liste da collect_all ikke virker for
        # ikke-installerede pakker (se sys.path.insert ovenfor)
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
| `ModuleNotFoundError: No module named 'mypkg.sub'` | `collect_submodules("mypkg.sub.deep")` inkluderer ikke forældrene `mypkg` og `mypkg.sub` | Brug `collect_submodules("mypkg")` — altid rodpakken |
| `ModuleNotFoundError` på lokalpakke trods `collect_submodules` i spec | `collect_submodules()` kører FØR `Analysis()` — `pathex` er ikke aktivt endnu. Lokale pakker der ikke er pip-installerede giver en tom liste. | Tilføj `sys.path.insert(0, os.path.abspath("."))` øverst i spec-filen + eksplicit modul-liste som sikkerhedsnet |
| `importlib.metadata.PackageNotFoundError: No package metadata was found for <pkg>` | `collect_data_files()` bundter datafiler men **ikke** dist-info-mappen. Kode der kalder `importlib.metadata.version()` / `requires()` ved runtime finder ingen metadata. | Brug `collect_all()` i stedet — det håndterer datas + binaries + hiddenimports + metadata i ét kald. For rene Python-pakker: `copy_metadata()` i `datas`. |
| Gentagne individuelle fejl med `collect_data_files` + `collect_submodules` + `copy_metadata` | Disse tre funktioner håndterer hver især kun én ting — det er let at glemme én. | Brug `collect_all("pkg")` fra starten — returnerer `(datas, binaries, hiddenimports)` og dækker det hele. |
| `PackageNotFoundError` for pakker man ikke kendte til (`cssselect`, `parsel` osv.) | Transitive afhængigheder bruger også `importlib.metadata` — manuel liste er aldrig komplet. | Brug en dynamisk løkke over `importlib.metadata.distributions()` i stedet for en hardkodet liste. |
| `ValueError` ved IP-validering på Windows (SSRF-tjek) | `socket.getaddrinfo()` returnerer IPv6-adresser med zone IDs (`fe80::1%eth0`) som `ip_address()` ikke kan parse | Wrap det indre `ip_address(sockaddr[0])`-kald i `try/except ValueError: continue` |
| `403 Resource not accessible by integration` i GitHub Actions | Token mangler skriveadgang til releases | Tilføj `permissions: contents: write` i workflow + sæt Read/write i repo-indstillinger |
| Scrapy finder 0 sider — `OSError: could not get source code` i hvert callback | Scrapy 2.15+ kalder `inspect.getsource()` på hvert callback for at opdage forældet `yield`-brug. I frozen app findes `.py`-kildefiler ikke (kun bytecode) — `getsource()` kaster `OSError` og Scrapy dropper hele responsen lydløst. | Monkey-patch `scrapy.utils.misc.is_generator_with_return_value` i `--scrapy-worker`-blokken til at returnere `False` ved `OSError` (se kodeeksempel nedenfor) |

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
git push origin main   # ALTID først — sikrer at origin har rettelserne
git tag v0.2.1         # nyt tag — peger på nuværende HEAD
git push origin v0.2.1 # trigger workflowet
```

Tagget trigger workflowet automatisk. Workflowet bruger workflow-filen **som den så ud på tag-tidspunktet** — tag derfor først efter alle fixes er committed og pushet til main.

### Kritisk misforståelse om tags

Et git-tag er en **fastfrossen peger på et bestemt commit**. `git push origin v0.2.0` sender tagget til GitHub, men bygger fra det commit tagget peger på — ikke fra den nyeste kode på main.

**Konsekvens:** Hvis du laver fixes *efter* at have sat et tag, og derefter pusher tagget igen, bygger GitHub Actions stadig fra den gamle kode. Du skal lave et **nyt tag** (f.eks. `v0.2.1`) der peger på HEAD efter fixet.

```
Commit A  ← tag v0.2.0  (bygger fra A — ingen fix)
Commit B  ← fix
Commit C  ← fix
           ← tag v0.2.1  (bygger fra C — med fixes)
```

---

## Windows-specifikke faldgruber i applikationskode

### SSRF-beskyttelse / IP-validering

Når du tjekker om en URL peger på en privat/intern adresse (SSRF-beskyttelse), er det fristende at skrive:

```python
from ipaddress import ip_address
import socket

hostname = urlparse(url).hostname or ""
try:
    ip = ip_address(hostname)          # fejler for domænenavne → ValueError
    ...
except ValueError:
    # Domænenavn — slå op og tjek den opløste IP
    for *_, sockaddr in socket.getaddrinfo(hostname, None):
        ip = ip_address(sockaddr[0])   # ← fejler på Windows!
        ...
```

**Problemet på Windows:** `socket.getaddrinfo()` kan returnere IPv6-adresser med zone IDs, f.eks. `fe80::1%eth0`. `ip_address("fe80::1%eth0")` kaster `ValueError` — som ikke er fanget i den indre løkke, og propagerer op som en uventet 500-fejl.

**Korrekt mønster:**

```python
try:
    ip = ip_address(hostname)
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        raise HTTPException(status_code=422, detail="Interne adresser er ikke tilladt")
except ValueError:
    try:
        resolved = socket.getaddrinfo(hostname, None)
        for *_, sockaddr in resolved:
            try:
                ip = ip_address(sockaddr[0])
            except ValueError:
                continue   # Windows IPv6 zone ID (fe80::1%eth0) — spring over
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise HTTPException(status_code=422, detail="Interne adresser er ikke tilladt")
    except socket.gaierror:
        pass   # kan ikke slås op — lad downstream håndtere det
```
