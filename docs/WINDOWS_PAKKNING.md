# Windows-pakkning af KlinikPortal

Plan for at distribuere KlinikPortal som en Windows-installer (`.exe`).
Endnu ikke implementeret — gemmes til et fremtidigt trin.

---

## Mål

Brugeren dobbeltklikker på `KlinikPortal-x.x.x-setup.exe` → installerer uden UAC-prompt → desktop-genvej → dobbelt-klik → browser åbner med appen. Ingen Python, ingen terminal, ingen teknisk opsætning på målmaskinen.

---

## Teknologi

| Værktøj | Formål |
|---|---|
| **PyInstaller ≥ 6.6** | Pakker Python 3.13 + alle dependencies ind i en program-mappe |
| **Inno Setup 6** | Laver den egentlige Windows-installer af program-mappen |
| **PowerShell-script** | Orkestrerer hele byggeprocessen |

> **Obs:** Bygningen skal foregå på en **Windows-maskine** (eller Windows CI/VM). Kan ikke bygges fra Linux.

---

## Det eneste svære problem — Scrapy som subprocess

I dag kører Scrapy som en subprocess via:
```python
cmd = [sys.executable, "-m", "scrapy", "crawl", ...]
```

I et frossent PyInstaller-miljø peger `sys.executable` på `KlinikPortal.exe`, ikke Python. Scrapy kan ikke startes på den måde.

### Løsning: "frozen executable as interpreter"-mønstret

Når appen er pakket, genbruges selve `.exe`-filen som Scrapy-interpreter via et skjult flag:

```
KlinikPortal.exe --scrapy-worker crawl site_spider -a start_url=... -a max_depth=...
```

`main.py` tjekker ved opstart om `--scrapy-worker` er i argumenterne:
- **Ja** → kør Scrapy CLI og afslut (ingen server startes)
- **Nej** → start FastAPI-serveren som normalt

---

## Filer der skal oprettes (nye)

| Fil | Beskrivelse |
|---|---|
| `KlinikPortal.spec` | PyInstaller-konfiguration: hidden imports, datas, noconsole |
| `build_windows.ps1` | Bygge-script: frontend → copy → PyInstaller → Inno Setup |
| `KlinikPortal.iss` | Inno Setup-script: installer, genveje, afinstaller |
| `backend/src/klinik/static/.gitkeep` | Sikrer mappen eksisterer i git |

---

## Kodeændringer i eksisterende filer (2 filer)

### `main.py` — dispatch-blok øverst

Tilføj **allerøverst** (før alle andre imports — kritisk pga. Twisted):

```python
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
```

### `backend/src/klinik/crawler/runner.py` — frozen-aware PROJECT_ROOT og subprocess

**Erstat linje 16:**
```python
# Var:
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Bliver:
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).parent
else:
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
```

**Erstat env + cmd i `start_crawl()`:**
```python
if getattr(sys, "frozen", False):
    cmd = [
        sys.executable, "--scrapy-worker",
        "crawl", "site_spider",
        "-a", f"start_url={url}",
        "-a", f"max_depth={depth}",
    ]
    env = {**os.environ, "SCRAPY_SETTINGS_MODULE": SCRAPY_SETTINGS}
else:
    cmd = [
        sys.executable, "-m", "scrapy", "crawl", "site_spider",
        "-a", f"start_url={url}",
        "-a", f"max_depth={depth}",
    ]
    env = {
        **os.environ,
        "SCRAPY_SETTINGS_MODULE": SCRAPY_SETTINGS,
        "PYTHONPATH": f"{PROJECT_ROOT}{os.pathsep}{PROJECT_ROOT / 'backend' / 'src'}",
    }
```

---

## PyInstaller-spec — nøglepunkter

```python
# pathex gør klinik-pakken importerbar
pathex=[".", "backend/src"]

# Ingen terminal-vindue
console=False

# Data der skal bundtes
datas=[
    ("backend/src/klinik/static/dist", "klinik/static/dist"),  # Vue-app
    ("assets/graph_template.html", "assets"),
    ("assets/hierarchy_template.html", "assets"),
    ("scrapy_crawler/scrapy.cfg", "scrapy_crawler"),
    *collect_data_files("scrapy"),
    *collect_data_files("twisted"),
    *collect_data_files("lxml"),
    *collect_data_files("certifi"),
]

# Kritiske hidden imports
# - collect_submodules("scrapy") + collect_submodules("twisted")  ← Twisted bruger string-opslag
# - uvicorn protokol-moduler (h11_impl, httptools_impl, websockets)
# - pydantic_core, pydantic_settings
# - lxml, lxml._elementpath
# - psutil._pswindows
# - pandas (collect_submodules)
# - scrapy_crawler.src.crawler.* (alle spider-moduler)
```

---

## Byggeprocessen (Windows)

```powershell
# Forudsætninger på build-maskinen:
# - Python 3.13 + uv
# - Node.js + npm
# - Inno Setup 6 (https://jrsoftware.org/isdl.php)

# Tilføj PyInstaller til dev-dependencies:
uv add --optional packaging pyinstaller>=6.6

# Kør bygge-scriptet:
.\build_windows.ps1
```

Scriptet:
1. `npm run build` i `frontend/`
2. Kopierer `frontend/dist/` → `backend/src/klinik/static/dist/`
3. Kører `pyinstaller KlinikPortal.spec --clean`
4. Kører `ISCC.exe KlinikPortal.iss` → `installer/KlinikPortal-0.1.0-setup.exe`

---

## Installer-konfiguration (Inno Setup)

- Installerer til `%LOCALAPPDATA%\Programs\KlinikPortal\` — **ingen UAC**
- Opretter `data/` og `data/exports/` mapper
- Tilbyder desktop-genvej og Start Menu-genvej
- `WorkingDir: {app}` på genveje (vigtigt for relativ `data/`-sti)
- Afinstaller: slår processen ihjel → fjerner filer

---

## Verifikation

### Test uden installer
```powershell
# Byg og test direkte:
.\build_windows.ps1
cd dist\KlinikPortal
.\KlinikPortal.exe
# → ingen terminal, browser åbner automatisk
```

### Test Scrapy-worker dispatch
```powershell
.\KlinikPortal.exe --scrapy-worker crawl site_spider -a start_url=https://example.com -a max_depth=1
# → Scrapy-log i terminalen, ingen server starter
```

### Kendte faldgruber

| Symptom | Årsag | Fix |
|---|---|---|
| Blank browser-side | `klinik/static/dist/index.html` mangler i bundle | Tjek copy-trin + `datas` i spec |
| Scrapy `ImportError` ved crawl | Manglende hidden import | Find modul i `_internal/`; tilføj til spec |
| `FileNotFoundError: assets/...` | Assets ikke bundtet | Tjek `datas`-tuple i spec |
| App starter slet ikke | PyInstaller < 6.6 med Python 3.13 | Opgrader PyInstaller |
| Antivirus-alarm | UPX-komprimering | Sæt `upx=False` i spec |
