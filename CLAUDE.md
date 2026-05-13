# KlinikPortal

Lokal desktop-app til Hellerup Laserklinik. FastAPI backend + Vue 3.5 SPA. Afløser LaserLink Mapper (CustomTkinter). Fase 3 tilføjer Gecko Booking API.

Crawler-koden (Scrapy-spider, pipeline, runner, analyse) er migreret fra `/workspaces/HellerupLaserklinik` (LaserLink Mapper) og tilpasset til dette projekt.

## Køre i dev

```bash
# Terminal 1 — backend
uv run python main.py          # FastAPI på :8765

# Terminal 2 — frontend
cd frontend && npm run dev     # Vite på :5173 (proxier /api → :8765)
```

## Linting / typetjek / tests

```bash
uv run ruff check .
uv run ruff format .
uv run mypy backend/
uv run --with pytest pytest
cd frontend && npm run type-check
```

## Vigtige stier

| Sti | Beskrivelse |
|---|---|
| `backend/src/klinik/` | Python-pakken — imports starter med `klinik.` |
| `scrapy_crawler/` | Scrapy-projekt, køres som subprocess |
| `data/config.json` | Indstillinger — aldrig i git |
| `data/klinik.db` | SQLite — aldrig i git |
| `assets/` | D3.js HTML-templates (graph + hierarchy) |
| `frontend/src/` | Vue 3.5 SPA |

## Scrapy manuelt

```bash
PYTHONPATH=. SCRAPY_SETTINGS_MODULE=scrapy_crawler.src.crawler.settings \
  uv run scrapy crawl site_spider -a start_url=https://example.com
```

## Porte og routing

- FastAPI: `:8765`
- Vite dev: `:5173`
- Frontend bruger `createWebHashHistory` → `/#/seo`, `/#/indstillinger` osv.

**Aktive ruter:** `/seo`, `/indstillinger`
**Fase 3-stubs (alle bruger `StubView.vue`):** `/oversigt`, `/bookinger`, `/statistik`, `/behandlinger`

**API-endpoints:**
- `GET /api/health`
- `GET /api/settings`, `PUT /api/settings` — `site_url`, `max_depth`
- `POST /api/crawler/start`, `POST /api/crawler/stop`, `GET /api/crawler/status`, `GET /api/crawler/results`
- `/api/gecko/*`, `/api/stats/*` — tomme placeholders (Fase 3)

## Frontend-struktur

```
layouts/AppLayout.vue          # shell: AppSidebar + inline header + RouterView
components/layout/AppSidebar.vue
components/layout/AppIcon.vue
components/seo/
  SeoControlBar.vue            # URL-input, start/stop, depth
  StatusStrip.vue              # live status-tekst under crawl
  SeoTabs.vue                  # tabs: Sider / Hierarki / Statistik
  PagesTable.vue               # side-tabel med StatusBadge + ProblemTag
  HierarchyTable.vue           # hierarki-tabel
  StatsTable.vue               # statistik-tabel
  StatusBadge.vue, ProblemTag.vue, ExportFooter.vue
views/SeoView.vue, SettingsView.vue, StubView.vue
stores/crawler.ts              # al crawler-logik (ingen separat composable)
stores/settings.ts
api/client.ts                  # ofetch base-instans
api/schemas.ts                 # Zod: CrawlPage, CrawlerStatus, CrawlerResults, AppSettings
```

Ingen `AppHeader.vue` (header er inline i `AppLayout.vue`). Ingen `api/crawler.ts` (kald sker i store). Ingen composables.

## Database-tabeller

```sql
crawl_pages  -- url, title, status_code, word_count, is_orphan, depth, parent_url, redirect_chain
crawl_links  -- source_url, target_url
gecko_cache_meta  -- endpoint, last_fetched, etag (Fase 3)
```

Backend crawler-analyse: `pipeline.py`, `broken_links.py`, `orphan_detector.py`, `depth_calculator.py`, `graph_builder.py`, `hierarchy_builder.py`, `exporter.py`

## Arkitektoniske beslutninger

| Beslutning | Valg |
|---|---|
| SPA routing | `createWebHashHistory` — ingen catch-all nødvendig |
| Fonte | `@fontsource/inter` + `@fontsource/jetbrains-mono` — offline |
| Tailwind | v4 via `@tailwindcss/vite` — ingen `tailwind.config.ts` |
| Scrapy stdout | Dedikeret daemon-tråd — forhindrer 64KB pipe-deadlock |
| SQLite | WAL mode (`PRAGMA journal_mode=WAL`) |
| `run_analysis()` | Wrapes i `asyncio.to_thread()` |
| Footer | I `SeoView`, ikke i `AppLayout` |
| shadcn-vue | Ikke brugt i Fase 2 |
| Error handling | Try/catch i alle store-actions, `error` ref i UI |

## Kendte begrænsninger

- Scrapy kører som subprocess i dev. PyInstaller-build kræver omskrivning til `CrawlerProcess` API.
- Gecko API integration er Fase 3 — `gecko/` og `statistics/` er placeholders.
