# Gecko Booking Statistik — Refined Plan

## Context

KlinikPortal har `/statistik` som en stub (StubView, sidebar disabled). Gecko Booking API-integration (Fase 3) aktiveres nu: backend henter bookinger via httpx, beregner kr/time, belægning og no-show, eksponerer 4 stats-endpoints + 3 gecko-endpoints. Frontend får en tabbed StatisticsView og Indstillinger-siden aktiverer det eksisterende (disabled) Gecko-token-felt.

**Kritiske kodebase-fund vs. draft-plan:**

- `Settings` i `config.py` har allerede `gecko_api_token` og `gecko_base_url` som felter — `save()` mangler bare parametren
- `SettingsView.vue` har allerede et Gecko Booking API-kort (linje 65–95) — men inputtet er `disabled`. Vi opdaterer det, skaber ikke et nyt kort
- `settings.ts` har allerede `geckoToken = ref('')` — men det er ikke forbundet til API (load/save). Vi bruger dette eksisterende felt
- `AppSettingsSchema` i `schemas.ts` mangler `gecko_api_token` — skal tilføjes for at settings-store kan loade token
- `selenium` er ikke i `pyproject.toml` — skal tilføjes

---

## Dependency-flow

```
gecko/models.py
    ↓
gecko/client.py ──────────────────┐
gecko/scraper.py                  │
    ↓                             │
gecko/router.py (3 endpoints)     │
                                  │
statistics/prices.py              │
statistics/service.py ←───────────┘
    ↓
statistics/models.py
statistics/router.py (4 endpoints)
    ↓
app.py (allerede mountet)

config.py.save() ← add gecko_api_token
app.py SettingsOut/In ← add gecko_api_token

schemas.ts ← AppSettingsSchema + stat schemas
settings.ts ← wire geckoToken to API
statistik.ts (new store)
StatisticsView.vue (new view)
router/index.ts ← /statistik → StatisticsView
AppSidebar.vue ← statistik: stubs[] → tools[]
SettingsView.vue ← enable token input + add price sync button
```

---

## Filer og ændringer

| Fil | Status | Ændring |
|-----|--------|---------|
| `backend/src/klinik/gecko/models.py` | **Ny** | Pydantic: Booking, BookingInterval, BookedTime, GeckoService, GeckoCalendar |
| `backend/src/klinik/gecko/client.py` | **Ny** | async httpx pagineret /booking fetch med Bearer token |
| `backend/src/klinik/gecko/scraper.py` | **Ny** | Selenium-scraper til listepriser + `_parse_price()` |
| `backend/src/klinik/gecko/router.py` | **Erstat** | POST /sync-prices, GET /prices-status, GET /prices |
| `backend/src/klinik/statistics/prices.py` | **Ny** | CSV-loader: data/behandlinger.csv → {navn: float} |
| `backend/src/klinik/statistics/service.py` | **Ny** | aggregate_volume, compute_efficiency, compute_providers |
| `backend/src/klinik/statistics/models.py` | **Ny** | Pydantic response-modeller |
| `backend/src/klinik/statistics/router.py` | **Erstat** | GET /bookings, /efficiency, /providers, /revenue |
| `backend/src/klinik/config.py` | **Opdater** | `save()` tilføj `gecko_api_token` parameter (linje 46–67) |
| `backend/src/klinik/app.py` | **Opdater** | `SettingsOut` + `SettingsIn` + handlers tilføj `gecko_api_token` |
| `pyproject.toml` | **Opdater** | Tilføj `"selenium>=4.20"` i `dependencies` |
| `tests/test_gecko_client.py` | **Ny** | duration_minutes unit tests (ingen httpx-mock) |
| `tests/test_gecko_scraper.py` | **Ny** | `_parse_price` unit tests (ingen Selenium) |
| `tests/test_stats_service.py` | **Ny** | aggregate_volume, compute_efficiency, compute_providers |
| `frontend/src/api/schemas.ts` | **Opdater** | AppSettingsSchema + gecko_api_token; tilføj stat-schemas |
| `frontend/src/stores/settings.ts` | **Opdater** | Wire eksisterende `geckoToken` til load/save (ikke nyt felt) |
| `frontend/src/stores/statistik.ts` | **Ny** | Pinia store: dateFrom/dateTo, loadAll(), syncPrices() |
| `frontend/src/views/StatisticsView.vue` | **Ny** | 4 tabs: Kr/time, Behandlere, Volumen, No-show |
| `frontend/src/router/index.ts` | **Opdater** | /statistik → StatisticsView (fjern heading/icon fra meta) |
| `frontend/src/components/layout/AppSidebar.vue` | **Opdater** | Flyt `statistik` fra `stubs[]` til `tools[]` |
| `frontend/src/views/SettingsView.vue` | **Opdater** | Aktiver eksisterende Gecko-felt (fjern `disabled`/Lock-icon), tilføj price-sync-knap |

---

## Implementeringsrækkefølge

### 1. Backend modeller og logik

**`gecko/models.py`** — ny fil:
```python
from __future__ import annotations
from pydantic import BaseModel, Field

class BookingInterval(BaseModel):
    from_: str = Field(alias="from")
    to: str
    def duration_minutes(self) -> int:
        fh, fm = map(int, self.from_.split(":"))
        th, tm = map(int, self.to.split(":"))
        return (th * 60 + tm) - (fh * 60 + fm)

class BookedTime(BaseModel):
    date: str
    interval: list[BookingInterval]

class GeckoService(BaseModel):
    serviceId: int | None = None
    serviceName: str | None = None

class GeckoCalendar(BaseModel):
    calendarId: int
    calendarName: str | None = None

class Booking(BaseModel):
    bookingId: int
    bookedTime: BookedTime
    service: GeckoService | None = None
    calendar: GeckoCalendar
    noShow: bool = False
    bookedOnline: bool = False
    createdDate: str | None = None
    createdTime: str | None = None
```

**`gecko/client.py`** — pagineret fetch via `settings.gecko_base_url` + `settings.gecko_api_token`.

**`statistics/prices.py`** — CSV-loader med dansk talformat (`1.900` → 1900.0).

**`statistics/service.py`** — `aggregate_volume()`, `compute_efficiency()`, `compute_providers()`.

**`statistics/models.py`** — Pydantic response-modeller for alle 4 endpoints.

### 2. Backend config + app

**`config.py`** — udvid `save()` med `gecko_api_token: str | None = None` parameter. `Settings` har allerede feltet, så vi behøver kun at tilføje det til `save()`-signaturen og den tilsvarende `data["gecko_api_token"]`-persistering og `self.gecko_api_token = gecko_api_token`-linje.

**`app.py`** — tilføj `gecko_api_token: str` til `SettingsOut`, `gecko_api_token: str | None = None` til `SettingsIn`, og opdater begge handlers.

### 3. Backend routers

**`gecko/router.py`** — erstatter placeholder. Tre endpoints:
- `POST /sync-prices` — starter Selenium i `asyncio.create_task()`, 409 hvis allerede kørende
- `GET /prices-status` — returnerer `{running, count, error}`
- `GET /prices` — returnerer `{prices: load_prices()}`

**`statistics/router.py`** — erstatter placeholder. Fire endpoints:
- `GET /bookings?start&end`
- `GET /efficiency?start&end`
- `GET /providers?start&end`
- `GET /revenue?start&end`

Alle checker `_require_token()` som rejser 400 hvis `settings.gecko_api_token` er tom.

### 4. pyproject.toml

Tilføj `"selenium>=4.20"` til `dependencies`-listen. Kør `uv sync`.

### 5. Tests

**`tests/test_gecko_client.py`** — tester `BookingInterval.duration_minutes()` direkte (ingen httpx-mock).

**`tests/test_gecko_scraper.py`** — tester `_parse_price()` (importerer kun én funktion, ingen Selenium).

**`tests/test_stats_service.py`** — tester alle tre service-funktioner med `make_booking()`-hjælpefunktion.

### 6. Frontend schemas

**`api/schemas.ts`** — to opdateringer:
1. Tilføj `gecko_api_token: z.string()` til `AppSettingsSchema` (backend eksponerer det nu)
2. Tilføj nye schemas til sidst: `BookingVolumeSchema`, `EfficiencyItemSchema`/`EfficiencyResponseSchema`, `ProviderStatsSchema`/`ProvidersResponseSchema`, `RevenueResponseSchema`, `PricesSyncStatusSchema` + tilsvarende `type`-exports.

### 7. Frontend settings store

**`stores/settings.ts`** — `geckoToken` eksisterer allerede. To ændringer:
1. I `load()`: tilføj `geckoToken.value = data.gecko_api_token ?? ''` (virker efter AppSettingsSchema er opdateret)
2. I `save()`: tilføj `gecko_api_token: geckoToken.value` i PUT-body

### 8. Frontend statistik store

**`stores/statistik.ts`** — ny Pinia setup-store med:
- `dateFrom`/`dateTo` refs (default: 90 dage tilbage → i dag)
- `volume`, `efficiency`, `providers`, `revenue` data-refs
- `loadAll()` — kalder alle 4 stats-endpoints parallelt med `Promise.all`
- `syncPrices()` + polling via `setInterval` mod `/gecko/prices-status`

### 9. Frontend view + routing

**`views/StatisticsView.vue`** — ny fil med 4 tabs (Kr/time, Behandlere, Volumen, No-show). Tabel-layout med horisontale bar-charts baseret på beregnede maks-værdier.

**`router/index.ts`** — erstat `/statistik`-ruten:
```typescript
// FØR:
{ path: '/statistik', component: StubView, meta: { ..., heading: 'Bookingstatistik', icon: 'Chart', ... } }
// EFTER:
{ path: '/statistik', component: StatisticsView, meta: { title: 'Statistik', sidebarKey: 'statistik' } }
```

**`AppSidebar.vue`** — flyt `statistik`-objektet fra `stubs[]` til `tools[]`. De øvrige stubs (`oversigt`, `bookinger`, `behandlinger`) forbliver i stubs.

**`SettingsView.vue`** — opdater det eksisterende Gecko Booking API-kort (linje 65–95):
- Fjern `disabled` attribut og `Lock`-ikonet fra inputtet
- Bind inputtet til `settings.geckoToken` (v-model)
- Fjern "Tilsluttes i en kommende opdatering."-teksten
- Fjern "Fase 3"-badge-chippen
- Tilføj en "Gem token"-knap der kalder `settings.save()`
- Tilføj en `<hr>` og prissync-sektion med "Opdater priser"-knap der kalder `statistik.syncPrices()`
- Tilføj `import { useStatistikStore } from '@/stores/statistik'` og `const statistik = useStatistikStore()` i `<script setup>`

---

## Verifikation

```bash
# 1. Backend unit tests
uv run --with pytest pytest tests/ -v
# Forventet: test_analysis.py, test_config.py + de 3 nye test-filer alle PASS

# 2. Import-sanity-check
uv run python -c "from klinik.app import app; print('OK')"

# 3. Type-check frontend
cd frontend && npm run type-check

# 4. Dev-servere
uv run python main.py          # Terminal 1
cd frontend && npm run dev     # Terminal 2

# 5. Manuel browser-test (http://localhost:5173)
# - /#/indstillinger: Gecko Booking API-felt er aktivt og kan udfyldes + gemmes
# - /#/statistik: viser StatisticsView (ikke StubView)
# - Sæt token, vælg periode, klik "Hent statistik" → 4 tabs med data
# - Statistik-linket i sidebar er klikbart (ikke grå/disabled)
# - "Opdater priser"-knap i Indstillinger starter scraping (kræver geckodriver)
```