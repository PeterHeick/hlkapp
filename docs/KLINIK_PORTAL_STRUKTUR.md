# KlinikPortal — Projektstruktur

## Tech stack

| Lag | Teknologi | Begrundelse |
|---|---|---|
| Frontend | Vue 3.5, TypeScript strict, Vite | Moderne, hurtig, god komponentmodel |
| Styling | Tailwind CSS + shadcn-vue | Professionelt look uden meget CSS |
| State | Pinia (setup stores) | Officiel Vue state manager |
| Routing | Vue Router 4 | Standard SPA-routing |
| API-klient | ofetch + Zod | Type-sikre API-kald med schema-validering |
| Backend | FastAPI (Python 3.13) | Hurtigt, automatisk API-dokumentation |
| Data | SQLite via `aiosqlite` | Ingen opsætning, kører lokalt |
| Gecko-klient | httpx (async) | Asynkrone HTTP-kald til Gecko API |
| Crawler | Scrapy + scrapy-playwright | Genanvendt fra LaserLink Mapper |
| Grafer | Apache ECharts (vue-echarts) | Rige interaktive grafer |
| Build | PyInstaller + Inno Setup | Windows `.exe`-installer |
| Python-styring | uv | Hurtig dependency management |
| Linting | Ruff (Python), ESLint + Prettier (JS) | |
| Typetjek | mypy (Python), tsc strict (TS) | |

---

## Mappestruktur

```
klinik-portal/
│
├── CLAUDE.md                        # Instruktioner til Claude Code
├── VISION.md                        # Formål og krav (se separat dokument)
├── README.md                        # Kom godt i gang
├── .python-version                  # 3.13
├── pyproject.toml                   # Python-projekt (hatchling, ruff, mypy)
├── uv.lock                          # Låste Python-afhængigheder
├── requirements.txt                 # Til PyInstaller CI-build
├── .gitignore
│
├── KlinikPortal.spec                # PyInstaller-build-konfiguration
├── installer.iss                    # Inno Setup-script → KlinikPortal-Setup.exe
│
├── main.py                          # Entry point: starter FastAPI + åbner browser
│
│── backend/                         # Python-backend (src-layout)
│   └── src/
│       └── klinik/
│           ├── __init__.py
│           ├── app.py               # FastAPI-app-instans, middleware, static files
│           ├── config.py            # Indstillinger via pydantic-settings (API-nøgle, port, stier)
│           ├── database.py          # SQLite init, get_connection()
│           │
│           ├── gecko/               # Gecko Booking API-integration
│           │   ├── __init__.py
│           │   ├── client.py        # httpx AsyncClient, auth-header, rate-limit
│           │   ├── models.py        # Pydantic-modeller (Booking, Service, Customer …)
│           │   ├── cache.py         # SQLite-cache: gemmer API-svar med TTL
│           │   └── router.py        # FastAPI-router: GET /api/gecko/bookings, /services …
│           │
│           ├── statistics/          # Aggregering og beregninger
│           │   ├── __init__.py
│           │   ├── bookings.py      # Omsætning pr. periode, belægningsgrad
│           │   ├── services.py      # Populære treatments, gennemsnitspriser
│           │   ├── customers.py     # Nye vs. tilbagevendende, kundegrupper
│           │   └── router.py        # FastAPI-router: GET /api/stats/…
│           │
│           └── crawler/             # SEO-crawler (logik lånt fra LaserLink)
│               ├── __init__.py
│               ├── runner.py        # start_crawl() / stop_crawl() via subprocess
│               ├── repository.py    # Læs crawl-resultater fra SQLite
│               └── router.py        # FastAPI-router: POST /api/crawler/start …
│
├── frontend/                        # Vue 3.5 TypeScript SPA
│   ├── package.json
│   ├── vite.config.ts               # Proxy /api → localhost:8765 i dev
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── components.json              # shadcn-vue konfiguration
│   ├── index.html
│   │
│   └── src/
│       ├── main.ts                  # Vue app bootstrap
│       ├── App.vue                  # Root-komponent, layout-shell
│       │
│       ├── router/
│       │   └── index.ts             # Ruter: /, /bookings, /statistics, /services,
│       │                            #         /seo, /settings
│       │
│       ├── stores/                  # Pinia stores (setup-stil)
│       │   ├── bookings.ts          # Booking-data, filtre, pagination
│       │   ├── statistics.ts        # Aggregeret statistik-state
│       │   ├── crawler.ts           # Crawler-status, fremskridt, resultater
│       │   └── settings.ts          # API-nøgle, URL, præferencer
│       │
│       ├── api/                     # Type-sikre API-kald (ofetch + Zod)
│       │   ├── client.ts            # Basis ofetch-instans
│       │   ├── gecko.ts             # Gecko-endpoints
│       │   ├── statistics.ts        # Statistik-endpoints
│       │   ├── crawler.ts           # Crawler-endpoints
│       │   └── schemas.ts           # Zod-skemaer (validering af API-svar)
│       │
│       ├── composables/             # Genbrugelig logik
│       │   ├── useDateRange.ts      # Periode-vælger logik
│       │   ├── useBookings.ts       # Booking-liste med filtre
│       │   └── useStatistics.ts     # Statistik-hentning og formatering
│       │
│       ├── views/                   # Route-niveau sider
│       │   ├── DashboardView.vue    # Overblik: nøgletal, mini-grafer
│       │   ├── BookingsView.vue     # Bookingsliste med filtre og søgning
│       │   ├── StatisticsView.vue   # Detaljerede grafer og tabeller
│       │   ├── ServicesView.vue     # Behandlinger og priser
│       │   ├── SeoView.vue          # Crawler-interface og resultater
│       │   └── SettingsView.vue     # API-nøgle, URL, præferencer
│       │
│       └── components/
│           ├── layout/
│           │   ├── AppSidebar.vue   # Venstre navigationsmenu
│           │   └── AppHeader.vue    # Topbar med periode-vælger og titel
│           │
│           ├── charts/              # ECharts-baserede grafkomponenter
│           │   ├── RevenueChart.vue      # Omsætning over tid (linje/søjle)
│           │   ├── BookingsByService.vue # Fordeling pr. behandling (pie/bar)
│           │   ├── OccupancyChart.vue    # Belægningsgrad pr. behandler
│           │   └── CustomerChart.vue     # Nye vs. tilbagevendende kunder
│           │
│           └── ui/                  # shadcn-vue primitive komponenter
│               └── (auto-genereret ved `npx shadcn-vue add …`)
│
├── assets/                          # D3.js HTML-templates (fra LaserLink)
│   ├── graph_template.html
│   └── hierarchy_template.html
│
├── scrapy_crawler/                  # Scrapy-projekt (lånt fra LaserLink)
│   ├── scrapy.cfg
│   └── src/
│       └── crawler/
│           ├── spiders/
│           │   └── site_spider.py
│           ├── pipelines.py
│           ├── settings.py
│           └── first_run.py
│
├── data/                            # Runtime-data (gitignored)
│   ├── klinik.db                    # SQLite: cached API-data + crawl-resultater
│   ├── config.json                  # API-nøgle + sidst brugte indstillinger
│   └── exports/                     # CSV-eksporter
│
├── logs/                            # Log-filer (gitignored)
│   └── klinik.log
│
└── .github/
    └── workflows/
        └── build.yml                # GitHub Actions: byg Windows-installer
```

---

## Hvordan frontend og backend hænger sammen

**Under udvikling (dev):**
```
npm run dev          → Vite starter på :5173
uv run python main.py → FastAPI starter på :8765

# vite.config.ts proxier /api/* → localhost:8765
# Så Vue-koden kalder bare /api/gecko/bookings
```

**I produktion (bygget):**
```
PyInstaller bundler FastAPI-serveren som LaserLink.exe
Vue bygges til statiske filer: npm run build → dist/
dist/-mappen kopieres ind i PyInstaller-bundlet
FastAPI server de statiske filer på / og API på /api/
Browseren åbnes automatisk på localhost:8765
```

---

## Database-tabeller (SQLite)

```sql
-- Gecko-cache (opdateres automatisk ved hentning)
gecko_bookings        -- id, start_time, end_time, service_id, customer_id, employee_id, status, cached_at
gecko_services        -- id, name, duration, price, group_id, cached_at
gecko_customers       -- id, name, email, phone, group_id, created_at, cached_at
gecko_employees       -- id, name, email, cached_at
gecko_cache_meta      -- endpoint, last_fetched, etag

-- Crawler-resultater
crawl_pages           -- url, title, status_code, word_count, is_orphan, depth, crawled_at
crawl_links           -- from_url, to_url, anchor_text, is_internal
```

---

## Kom godt i gang (udvikling)

```bash
# Python-backend
uv sync
uv run python main.py

# Vue-frontend (separat terminal)
cd frontend
npm install
npm run dev

# Åbn browser på http://localhost:5173
```

## Byg Windows-installer

```bash
# Frontend skal bygges først
cd frontend && npm run build
cp -r dist/ ../backend/src/klinik/static/

# Derefter PyInstaller + Inno Setup (eller via GitHub Actions)
uv run pyinstaller KlinikPortal.spec --clean --noconfirm
ISCC.exe installer.iss
# Output: installer/KlinikPortal-Setup.exe
```

---

## Filer der ikke må i git

```gitignore
data/
logs/
*.db
config.json
.env
frontend/node_modules/
frontend/dist/
backend/src/klinik/static/dist/
__pycache__/
dist/
build/
installer/
*.spec.bak
```

---

## GitHub Actions

CI-pipeline (`build.yml`) kører automatisk ved push til `main` eller ved tag `v*.*.*`:

1. Byg Vue-frontend (`npm run build`)
2. Kopier Vue-dist ind i Python-pakken
3. Kør PyInstaller
4. Kør Inno Setup
5. Upload `KlinikPortal-Setup.exe` som artifact
6. Publicér GitHub Release ved tag (til download)
