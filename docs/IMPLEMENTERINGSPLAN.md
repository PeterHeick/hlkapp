# KlinikPortal — Implementeringsplan (autoritativ)

> Dette dokument erstatter `DESIGN_IMPLEMENTERING.md` og tidligere versioner.
> Alle arkitektoniske beslutninger er låst her.

---

## Faser

| Fase | Navn | Status |
|---|---|---|
| 1 | Design | ✅ Færdig (design i `docs/hlkapp_design/`) |
| 2 | HellerupLaserklinik migration | 🔄 I gang |
| 3 | Gecko API integration | ⏳ Ikke startet |

---

## Acceptance-kriterier for Fase 2 (definition of done)

Fase 2 er færdig når:
1. `uv run python main.py` starter FastAPI på :8765 og åbner browser
2. `cd frontend && npm run dev` starter Vite på :5173 uden fejl
3. Crawler starter ved klik på "Start crawl" med en gyldig URL
4. Sider vises i Tab 1 efter crawl er færdig
5. Tab 2 (Sidestatistik) viser sortérbare kolonner
6. Tab 3 (Hierarki) viser top-stier
7. Alle tre CSV-eksporter downloader en fil
8. "Åbn interaktiv graf" og "Åbn hierarki-træ" åbner D3.js HTML i nyt vindue
9. Indstillinger gemmes og geninlæses ved genstart
10. Tidligere crawl-session gendannes ved app-start (hvis DB har sider)

---

## Låste arkitektoniske beslutninger

| Beslutning | Valg | Begrundelse |
|---|---|---|
| SPA routing | `createWebHashHistory` | Lokal app, ingen server-side catch-all nødvendig |
| Fonte | npm-pakker (`@fontsource/inter`, `@fontsource/jetbrains-mono`) | Offline-støtte — ingen CDN |
| Tailwind | v4 via `@tailwindcss/vite` plugin | CSS-baseret config, ingen `tailwind.config.ts` |
| Scrapy stdout | Dedikeret daemon-tråd i `router.py` ved start | Forhindrer 64KB pipe-deadlock |
| SQLite WAL | `PRAGMA journal_mode=WAL` i `database.py` | Concurrent writes fra Scrapy + analyse |
| Crawl reset | `repo.reset()` kaldes i `POST /api/crawler/start` | Rydder gammel data før ny crawl |
| analyse() wrapping | `asyncio.to_thread()` i alle synkrone DB/pandas-kald | Blokerer ikke FastAPI event loop |
| Footer-placering | `ExportFooter` i `SeoView`, ikke i `AppLayout` | `AppLayout` har ingen footer-slot |
| shadcn-vue | Ikke brugt i Fase 2 | Designet er self-contained Tailwind |
| Composables | Ingen `useCrawler.ts` — al logik i Pinia store | Enklere, ingen dobbelt-ansvar |
| Finish-guard | Mutex-flag i crawler store | Forhindrer dobbelt-kald fra poll + stop |
| Error handling | Try/catch i alle store actions, fejl sættes i `error: ref` | Brugeren ser fejlbesked i UI |
| Hierarki-beregning | Backend (`hierarchy_builder.py`) genererer HTML, frontend beregner tabel-summary | Begge er nødvendige: backend til D3-graf, frontend til Tab 3-tabel |

---

## Design tokens

```
Sidebar:       #0f172a
Main bg:       bg-slate-50
Kort:          bg-white
Accent:        indigo-600
Start-knap:    emerald-600 / 700
Stop-knap:     rose-600 / 700
Rækkekoder:
  ok:     bg-white + border-l-transparent
  orphan: bg-amber-50/40 + border-l-amber-400
  error:  bg-rose-50/40 + border-l-rose-500
  deep:   bg-sky-50/40 + border-l-sky-400
Font body: Inter (via @fontsource/inter)
Font mono: JetBrains Mono (via @fontsource/jetbrains-mono)
```

---

## Komponent-hierarki (autoritativt)

```
App.vue
└── layouts/AppLayout.vue
    ├── components/layout/AppSidebar.vue
    │   └── components/layout/AppIcon.vue
    └── <RouterView>
        ├── views/SeoView.vue
        │   ├── components/seo/SeoControlBar.vue
        │   ├── components/seo/StatusStrip.vue
        │   ├── components/seo/SeoTabs.vue
        │   │   ├── components/seo/PagesTable.vue
        │   │   │   ├── components/seo/StatusBadge.vue
        │   │   │   └── components/seo/ProblemTag.vue
        │   │   ├── components/seo/StatsTable.vue
        │   │   │   └── components/seo/StatusBadge.vue
        │   │   └── components/seo/HierarchyTable.vue
        │   └── components/seo/ExportFooter.vue   ← i bunden af SeoView
        ├── views/SettingsView.vue
        └── views/StubView.vue  (genbruges til 4 Gecko-stubs)
```

---

## Filstruktur (komplet)

```
hlkapp/
├── .devcontainer/
│   ├── devcontainer.json        ← Python 3.13, porte, volumes
│   └── project-setup.sh        ← uv sync, data/, config.json
├── docs/                        ← planer og design
├── .python-version              ← 3.13
├── pyproject.toml               ← hatchling, deps, ruff, mypy
├── .gitignore
├── CLAUDE.md
├── main.py                      ← starter FastAPI + browser
│
├── backend/
│   └── src/
│       └── klinik/
│           ├── __init__.py
│           ├── config.py        ← pydantic-settings
│           ├── database.py      ← SQLite init + WAL
│           ├── app.py           ← FastAPI app
│           ├── crawler/
│           │   ├── __init__.py
│           │   ├── db.py        ← migr. HellerupLaserklinik
│           │   ├── repository.py
│           │   ├── runner.py    ← subprocess + drain-tråd
│           │   ├── router.py    ← alle crawler-endpoints
│           │   └── analysis/
│           │       ├── __init__.py
│           │       ├── pipeline.py
│           │       ├── broken_links.py
│           │       ├── depth_calculator.py
│           │       ├── exporter.py
│           │       ├── graph_builder.py
│           │       ├── hierarchy_builder.py
│           │       └── orphan_detector.py
│           ├── gecko/           ← PLACEHOLDER Fase 3
│           │   ├── __init__.py
│           │   └── router.py
│           └── statistics/      ← PLACEHOLDER Fase 3
│               ├── __init__.py
│               └── router.py
│
├── scrapy_crawler/
│   ├── scrapy.cfg
│   └── src/
│       └── crawler/
│           ├── __init__.py
│           ├── db.py
│           ├── pipelines.py
│           ├── settings.py
│           └── spiders/
│               ├── __init__.py
│               └── site_spider.py
│
├── assets/
│   ├── graph_template.html
│   └── hierarchy_template.html
│
└── frontend/
    ├── package.json
    ├── vite.config.ts           ← @tailwindcss/vite + /api proxy
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.ts
        ├── style.css            ← @import 'tailwindcss' + kp-indeterminate
        ├── App.vue
        ├── router/
        │   └── index.ts         ← createWebHashHistory, danske ruter
        ├── stores/
        │   ├── crawler.ts       ← finish-guard, error-state
        │   └── settings.ts
        ├── api/
        │   ├── client.ts
        │   └── schemas.ts       ← Zod-skemaer
        ├── layouts/
        │   └── AppLayout.vue
        ├── components/
        │   ├── layout/
        │   │   ├── AppSidebar.vue
        │   │   └── AppIcon.vue
        │   └── seo/
        │       ├── SeoControlBar.vue
        │       ├── StatusStrip.vue
        │       ├── SeoTabs.vue
        │       ├── PagesTable.vue
        │       ├── StatsTable.vue
        │       ├── HierarchyTable.vue
        │       ├── StatusBadge.vue
        │       ├── ProblemTag.vue
        │       └── ExportFooter.vue
        └── views/
            ├── SeoView.vue
            ├── SettingsView.vue
            └── StubView.vue
```

---

## Backend API-endpoints

| Endpoint | Metode | Body / Response |
|---|---|---|
| `/api/health` | GET | `{ status: "ok", version: "0.1.0" }` |
| `/api/settings` | GET | `{ site_url, max_depth, port }` |
| `/api/settings` | PUT | Body: `{ site_url, max_depth }` |
| `/api/crawler/start` | POST | Body: `{ url, depth }` → starter crawl + drain-tråd |
| `/api/crawler/stop` | POST | Stopper subprocess + børneprocesser |
| `/api/crawler/status` | GET | `{ running, page_count, log_tail: string[] }` |
| `/api/crawler/results` | GET | `{ pages: [...], link_counts: { url: {in,out} } }` |
| `/api/crawler/export/inventory` | GET | CSV StreamingResponse |
| `/api/crawler/export/matrix` | GET | CSV StreamingResponse |
| `/api/crawler/export/todo` | GET | CSV StreamingResponse |
| `/api/crawler/graph` | GET | Redirect til `data/graph.html` (FileResponse) |
| `/api/crawler/hierarchy` | GET | Redirect til `data/hierarchy.html` (FileResponse) |

**Bemærk `/api/crawler/results`:** Returnerer `link_counts` som aggregerede tal (ikke rå links) — beregnet i backend med SQL COUNT queries. Frontend henter ikke rå link-data.

---

## Zod-skemaer

```typescript
CrawlPageSchema:    { url, status_code, depth, is_orphan, title?, word_count }
CrawlLinkCountSchema: { url, inbound, outbound }
CrawlerStatusSchema:  { running, page_count, log_tail }
AppSettingsSchema:    { site_url, max_depth, port }
```

---

## Crawler-store finish-guard

```typescript
let finishing = false

async function finish() {
  if (finishing) return   // guard mod dobbelt-kald
  finishing = true
  try {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
    running.value = false
    await loadResults()
    statusText.value = `Analyse færdig — ${orphanCount.value} forældreløse · ${errorCount.value} fejl`
  } finally {
    finishing = false
  }
}
```

---

## Scrapy stdout-drain (runner.py)

```python
def _drain_stdout(proc: subprocess.Popen, log_buffer: collections.deque) -> None:
    """Læs subprocess stdout linje for linje — forhindrer 64KB pipe-deadlock."""
    for line in proc.stdout:
        stripped = line.rstrip()
        if stripped:
            log_buffer.append(stripped)
            logger.debug("[scrapy] %s", stripped)
```

Startes som `threading.Thread(target=_drain_stdout, args=(proc, _log_buffer), daemon=True).start()` i `start_crawl()`.

---

## CSS-animation

```css
/* src/style.css */
@import 'tailwindcss';

@keyframes kp-indeterminate {
  0%   { left: -40%; width: 40%; }
  60%  { left: 100%; width: 40%; }
  100% { left: 100%; width: 40%; }
}
.kp-indeterminate {
  position: absolute;
  animation: kp-indeterminate 1.4s ease infinite;
  background: linear-gradient(90deg, transparent, #6366f1, transparent);
  inset-block: 0;
}
```

---

## Minimale tests (Fase 2)

```
tests/
├── test_analysis.py     ← find_orphans, find_broken_links med fixture-data
├── test_crawler_api.py  ← FastAPI TestClient: /start, /stop, /status, /results
└── test_config.py       ← Settings loader
```

Køres med: `uv run pytest`

---

## Ruter (frontend)

```typescript
// createWebHashHistory — URLs: /#/seo, /#/indstillinger osv.
/           → redirect /#/seo
/#/seo      → SeoView       (meta: { title, sidebarKey: 'seo' })
/#/indstillinger → SettingsView (meta: { title, sidebarKey: 'indstillinger' })
// Fase 3 stubs:
/#/oversigt    → StubView
/#/bookinger   → StubView
/#/statistik   → StubView
/#/behandlinger → StubView
```

---

## Fase 3 — Gecko API (ikke startet)

Se kendte begrænsninger i `docs/KLINIK_PORTAL_VISION.md` og memory-filer.
Tilføjes ved at udfylde placeholders i `gecko/` og `statistics/` — ingen Fase 2-kode røres.

---

## Implementeringsrækkefølge

```
[✓] Fase 1 — Design
[ ] Devcontainer-opdatering
[ ] Python-projektfiler (pyproject.toml, .python-version, CLAUDE.md, main.py)
[ ] Backend kerne (config, database, app)
[ ] Scrapy-migration (scrapy_crawler/ + backend/crawler/analysis/)
[ ] Crawler backend-modul (db, repository, runner, router)
[ ] Assets kopieres
[ ] Frontend setup (vite, tailwind v4, fonte)
[ ] Frontend API-lag + stores + router
[ ] Layout-komponenter (AppLayout, AppSidebar, AppIcon)
[ ] SEO-komponenter (badges, tabeller, controlbar, tabs, footer)
[ ] Views (SeoView, SettingsView, StubView)
[ ] Smoke-test: backend + frontend kører + crawl virker
[ ] Minimale tests
```
