# KlinikPortal — Design-implementeringsplan

Baseret på designfilen `docs/hlkapp_design/components.jsx`.

---

## Design tokens (udtræk fra designet)

```
Farver:
  Sidebar baggrund:  #0f172a            (bg-[#0f172a])
  Main baggrund:     bg-slate-50
  Indholdskort:      bg-white
  Accent/primær:     indigo-600         (tabs, save-knap, fokus-ring)
  Start-knap:        emerald-600 / emerald-700
  Stop-knap:         rose-600 / rose-700
  Rækkekoder:
    ok:      bg-white + border-l-transparent
    orphan:  bg-amber-50/40 + border-l-amber-400
    error:   bg-rose-50/40  + border-l-rose-500
    deep:    bg-sky-50/40   + border-l-sky-400

Skrifttyper:
  Body:  Inter, system-ui, sans-serif
  URLs:  JetBrains Mono, ui-monospace, monospace

Størrelser:
  Header-bar:      h-[56px]
  Control-bar:     h-[56px]
  Status-strip:    h-[40px]
  Footer:          h-[52px]
  Sidebar:         w-[220px]
  Tabelrækker:     py-1.5  (~28-32px effektiv højde)
  Fontstørrelser:  11px – 15px (meget kompakt)
```

---

## Komponent-hierarki (Vue-mapping)

```
App.vue
└── layouts/AppLayout.vue            ← Shell fra designet
    ├── AppSidebar.vue               ← Sidebar-komponent
    └── router-view
        ├── SeoView.vue              ← SeoScreen fra designet
        │   ├── SeoControlBar.vue
        │   ├── StatusStrip.vue
        │   ├── SeoTabs.vue
        │   └── (tab-indhold)
        │       ├── PagesTable.vue   ← Tab 1
        │       ├── StatsTable.vue   ← Tab 2
        │       └── HierarchyTable.vue ← Tab 3
        ├── SettingsView.vue         ← SettingsScreen fra designet
        └── StubView.vue             ← StubScreen (Oversigt/Bookinger/Statistik/Behandlinger)
```

---

## Fil for fil

### `src/App.vue`
```vue
<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
</script>

<template>
  <AppLayout />
</template>
```

### `src/layouts/AppLayout.vue`
Svarer til `Shell`-komponenten i designet.

```vue
<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title as string ?? '')
</script>

<template>
  <div class="flex h-screen bg-slate-50" style="font-family: Inter, system-ui, sans-serif">
    <AppSidebar />
    <main class="flex-1 min-w-0 flex flex-col">
      <header class="h-[56px] shrink-0 bg-white border-b border-slate-200 px-6 flex items-center">
        <h1 class="text-[15px] font-semibold text-slate-900 tracking-tight">{{ title }}</h1>
      </header>
      <div class="flex-1 min-h-0 flex flex-col">
        <RouterView />
      </div>
    </main>
  </div>
</template>
```

Props fra Shell der håndteres via `route.meta`: `title`, `breadcrumb`.

---

### `src/components/layout/AppSidebar.vue`
Svarer til `Sidebar`-komponenten. Ingen props — bruger `useRoute()` til at bestemme aktiv rute.

**Nøgle Tailwind-klasser fra designet:**
- Aktiv nav-item: `bg-indigo-500/15 text-white ring-1 ring-inset ring-indigo-400/25`
- Aktiv ikon: `text-indigo-300`
- Inaktiv item: `text-slate-300 hover:bg-slate-800/60 hover:text-white`
- Stub-item: `text-slate-500/70 cursor-not-allowed`
- Brand logo: `bg-gradient-to-br from-indigo-400 to-indigo-600`
- Status-dot: `w-1.5 h-1.5 rounded-full bg-emerald-400`

**Nav-items:**
```typescript
const tools = [
  { key: 'seo',      path: '/seo',      Icon: Globe,    label: 'SEO & Hjemmeside' },
  { key: 'settings', path: '/settings', Icon: Settings, label: 'Indstillinger' },
]

const stubs = [
  { key: 'oversigt',    Icon: Dashboard, label: 'Oversigt' },
  { key: 'bookinger',   Icon: Calendar,  label: 'Bookinger' },
  { key: 'statistik',   Icon: Chart,     label: 'Statistik' },
  { key: 'behandlinger',Icon: Scissors,  label: 'Behandlinger' },
]
```

**Icons:** Inline SVG-komponenter (lucide-stil). Fra designet er paths:
- `Spark` (brand): starburst/laser-stråler
- `Globe` (SEO): circle + 2 longitude-linjer
- `Settings`: gear
- `Dashboard`: 4 rektangler
- `Calendar`: rekt + 2 datostreger + linje
- `Chart`: axes + linjegraf
- `Scissors`: 2 cirkler + krydslinje
- `Network` (graf): 3 cirkler + linjer
- `Sitemap` (hierarki): 3 rektangler + linjer

Lav én `AppIcon.vue`-komponent der accepterer `name`-prop og renderer den rigtige SVG.

---

### `src/views/SeoView.vue`
Top-level view. Svarer til `SeoScreen`. Koordinerer crawler-state via `useCrawlerStore()`.

```vue
<script setup lang="ts">
import { useCrawlerStore } from '@/stores/crawler'
import SeoControlBar from '@/components/seo/SeoControlBar.vue'
import StatusStrip from '@/components/seo/StatusStrip.vue'
import SeoTabs from '@/components/seo/SeoTabs.vue'
import ExportFooter from '@/components/seo/ExportFooter.vue'

const crawler = useCrawlerStore()
</script>

<template>
  <SeoControlBar
    v-model:url="crawler.url"
    :depth="crawler.depth"
    :crawling="crawler.running"
    @start="crawler.start()"
    @stop="crawler.stop()"
  />
  <StatusStrip
    :status="crawler.statusText"
    :count="crawler.pageCount"
    :crawling="crawler.running"
  />
  <SeoTabs />
  <template #footer>
    <ExportFooter />
  </template>
</template>
```

---

### `src/components/seo/SeoControlBar.vue`
Svarer til `SeoControlBar` fra designet.

**Props:**
```typescript
defineProps<{
  url: string
  depth: number
  crawling: boolean
}>()

defineEmits<{
  'update:url': [value: string]
  start: []
  stop: []
}>()
```

**Tailwind nøgle-klasser:**
- URL-input: `w-full h-9 px-3 pr-9 rounded-md bg-slate-50 border border-slate-300 text-[13px] font-mono`
- Focus: `focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400`
- Start (aktiv): `h-9 px-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md text-[13px] font-semibold`
- Start (disabled): `bg-emerald-600/40 text-white/70 cursor-not-allowed`
- Stop (aktiv): `bg-rose-600 hover:bg-rose-700 text-white`
- Stop (disabled): `bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200`

---

### `src/components/seo/StatusStrip.vue`
Svarer til `StatusStrip`. Viser crawl-status, progress-bar og sidetal.

**Props:** `status: string`, `count: number`, `crawling: boolean`

**Progress-bar:**
- Crawling: gradient-animation (indeterminate) — `kp-indeterminate` CSS-animation
- Færdig: `bg-emerald-500 w-full`

**CSS-animation (i `main.css`):**
```css
@keyframes kp-indeterminate {
  0%   { left: -40%; width: 40% }
  60%  { left: 100%; width: 40% }
  100% { left: 100%; width: 40% }
}
.kp-indeterminate {
  animation: kp-indeterminate 1.4s ease infinite;
  position: absolute;
}
```

---

### `src/components/seo/SeoTabs.vue`
Svarer til `Tabs` + tab-indhold (de tre tabs).

**State:** `activeTab = ref(0)` (lokal)

**Tab-understreg:** `absolute inset-x-2 -bottom-px h-0.5 bg-indigo-600 rounded-t`

**Tab-indhold:**
- Tab 0 (`PagesTable`) — viser `crawler.pages` (fra store)
- Tab 1 (`StatsTable`) — viser `crawler.pages` med ekstra kolonner
- Tab 2 (`HierarchyTable`) — viser `crawler.hierarchySummary` (beregnet i store)

---

### `src/components/seo/PagesTable.vue`
Svarer til `PagesTable`. Viser Tab 1.

**Type:**
```typescript
interface CrawlPage {
  url: string
  status_code: number
  depth: number
  is_orphan: boolean
  title: string | null
  word_count: number
}
```

**Rækkeklasser** (fra `rowClasses`-funktionen i designet):
```typescript
function rowClass(page: CrawlPage): string {
  if (page.is_orphan) return 'bg-amber-50/40 border-l-[3px] border-l-amber-400'
  if (page.status_code >= 400) return 'bg-rose-50/40 border-l-[3px] border-l-rose-500'
  if (page.depth > 4) return 'bg-sky-50/40 border-l-[3px] border-l-sky-400'
  return 'bg-white border-l-[3px] border-l-transparent'
}
```

**`StatusBadge`-komponent** (genbruges i Tab 1 og Tab 2):
- 200-299: `bg-emerald-50 text-emerald-700 ring-emerald-200` + Check-ikon
- 300-399: `bg-amber-50 text-amber-700 ring-amber-200` + ArrowUp-ikon
- 400+: `bg-rose-50 text-rose-700 ring-rose-200` + XCircle-ikon

**`ProblemTag`-komponent:**
- `orphan`: amber, AlertTri-ikon, "Forældreløs"
- `error`: rose, XCircle-ikon, "Fejl 404"
- `deep`: sky, ArrowDown-ikon, "Dyb side"
- `redir`: amber, ArrowUp-ikon, "Omdirigeret"
- `none`: `—` i text-slate-400

---

### `src/components/seo/StatsTable.vue`
Svarer til `StatsTable` (Tab 2). Sortérbare kolonner.

**Kolonner:** URL, Titel, Status, Dybde, Indgående, Udgående, Ord, Forældrelos

**Sortering:**
```typescript
const sortKey = ref<keyof CrawlPageStats>('depth')
const sortDir = ref<'asc' | 'desc'>('asc')

const sorted = computed(() =>
  [...props.rows].sort((a, b) => {
    const v = sortDir.value === 'asc' ? 1 : -1
    return a[sortKey.value] > b[sortKey.value] ? v : -v
  })
)
```

Indgående/udgående links beregnes i Pinia-storen ved at tælle `crawl_links`.

---

### `src/components/seo/HierarchyTable.vue`
Svarer til `HierarchyTable` (Tab 3). Tre kolonner: Top-sti, Undersider, Maks. dybde.

Beregnes i `useCrawlerStore.hierarchySummary`:
```typescript
const hierarchySummary = computed(() => {
  const map = new Map<string, { count: number; maxDepth: number }>()
  for (const page of pages.value) {
    const parts = new URL(page.url).pathname.split('/').filter(Boolean)
    const top = parts.length ? '/' + parts[0] : '/'
    const entry = map.get(top) ?? { count: 0, maxDepth: 0 }
    entry.count++
    entry.maxDepth = Math.max(entry.maxDepth, page.depth)
    map.set(top, entry)
  }
  return [...map.entries()].map(([path, v]) => ({ path, ...v }))
})
```

**Tab 3 toolbar:** "Åbn hierarki-træ"-knap → `window.open('/api/crawler/hierarchy')` (serverer den genererede HTML-fil).

---

### `src/components/seo/ExportFooter.vue`
Tre outline-knapper med Save-ikon. Kalder `GET /api/crawler/export/inventory`, `/matrix`, `/todo` som fil-downloads.

```typescript
async function download(type: 'inventory' | 'matrix' | 'todo') {
  const url = `/api/crawler/export/${type}`
  const a = document.createElement('a')
  a.href = url
  a.download = `${type}.csv`
  a.click()
}
```

---

### `src/views/SettingsView.vue`
Svarer til `SettingsScreen`. To sektionskort.

**Sektion 1 — Hjemmeside:**
- `site_url`: text input (monospace font)
- `max_depth`: number input, 2–8

**Sektion 2 — Gecko Booking API:**
- Viser "Fase 3"-badge
- API token-felt: disabled, `cursor-not-allowed`, Lock-ikon

**Gem:**
```typescript
async function save() {
  await apiFetch('/api/settings', { method: 'PUT', body: form })
  // Toast-besked
}
```

---

### `src/views/StubView.vue`
Genbruges til alle fire Gecko-stubs. Modtager `title`, `heading`, `icon` via route meta.

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div class="flex-1 flex items-center justify-center bg-slate-50 px-6">
    <div class="text-center max-w-md">
      <div class="mx-auto mb-5 w-20 h-20 rounded-2xl bg-white border border-slate-200 shadow-sm
                  flex items-center justify-center text-slate-300">
        <AppIcon :name="route.meta.icon" :size="40" :stroke="1.5" />
      </div>
      <h2 class="text-[20px] font-semibold text-slate-800 tracking-tight">
        {{ route.meta.heading }}
      </h2>
      <p class="mt-2 text-[13.5px] text-slate-500 leading-relaxed">
        Denne funktion tilsluttes Gecko Booking API i en kommende opdatering.
      </p>
      <span class="inline-flex items-center gap-1.5 mt-5 px-2.5 py-1 rounded-full
                   bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-200
                   text-[11.5px] font-semibold uppercase tracking-wider">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500" />
        Fase 3
      </span>
    </div>
  </div>
</template>
```

---

## Pinia stores

### `src/stores/crawler.ts`

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api/client'

export const useCrawlerStore = defineStore('crawler', () => {
  // State
  const url = ref('')
  const depth = ref(5)
  const running = ref(false)
  const pageCount = ref(0)
  const statusText = ref('Klar')
  const pages = ref<CrawlPage[]>([])
  const links = ref<CrawlLink[]>([])

  // Polling interval-ref
  let pollTimer: ReturnType<typeof setInterval> | null = null

  // Computed
  const orphanCount = computed(() => pages.value.filter(p => p.is_orphan).length)
  const errorCount = computed(() => pages.value.filter(p => p.status_code >= 400).length)
  const hierarchySummary = computed(() => { /* se ovenfor */ })

  // Inbound/outbound link counts til StatsTable
  const inboundCount = computed(() => {
    const map = new Map<string, number>()
    for (const l of links.value) map.set(l.target_url, (map.get(l.target_url) ?? 0) + 1)
    return map
  })
  const outboundCount = computed(() => {
    const map = new Map<string, number>()
    for (const l of links.value) map.set(l.source_url, (map.get(l.source_url) ?? 0) + 1)
    return map
  })

  // Actions
  async function start() {
    running.value = true
    statusText.value = `Crawling: ${url.value}`
    pages.value = []
    links.value = []
    pageCount.value = 0
    await apiFetch('/api/crawler/start', { method: 'POST', body: { url: url.value } })
    pollTimer = setInterval(poll, 2000)
  }

  async function stop() {
    await apiFetch('/api/crawler/stop', { method: 'POST' })
    finish()
  }

  async function poll() {
    const status = await apiFetch<CrawlerStatus>('/api/crawler/status')
    pageCount.value = status.page_count
    if (!status.running) finish()
  }

  async function finish() {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
    running.value = false
    await loadResults()
    statusText.value = `Analyse færdig — ${orphanCount.value} forældreløse · ${errorCount.value} fejl`
  }

  async function loadResults() {
    const data = await apiFetch<{ pages: CrawlPage[]; links: CrawlLink[] }>('/api/crawler/results')
    pages.value = data.pages
    links.value = data.links
    pageCount.value = data.pages.length
  }

  // Indlæs tidligere session ved app-start
  async function restoreSession() {
    const status = await apiFetch<CrawlerStatus>('/api/crawler/status')
    if (status.page_count > 0) {
      await loadResults()
      statusText.value = `Tidligere session indlæst — ${pages.value.length} sider`
    }
  }

  return {
    url, depth, running, pageCount, statusText, pages, links,
    orphanCount, errorCount, hierarchySummary, inboundCount, outboundCount,
    start, stop, loadResults, restoreSession,
  }
})
```

### `src/stores/settings.ts`

```typescript
export const useSettingsStore = defineStore('settings', () => {
  const siteUrl = ref('')
  const maxDepth = ref(5)
  const geckoToken = ref('')    // Fase 3 — tomt felt

  async function load() {
    const data = await apiFetch<AppSettings>('/api/settings')
    siteUrl.value = data.site_url
    maxDepth.value = data.max_depth
  }

  async function save() {
    await apiFetch('/api/settings', {
      method: 'PUT',
      body: { site_url: siteUrl.value, max_depth: maxDepth.value }
    })
  }

  return { siteUrl, maxDepth, geckoToken, load, save }
})
```

---

## Router

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import SeoView from '@/views/SeoView.vue'
import SettingsView from '@/views/SettingsView.vue'
import StubView from '@/views/StubView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          redirect: '/seo' },
    {
      path: '/seo',
      component: SeoView,
      meta: { title: 'SEO & Hjemmeside', breadcrumb: 'Crawl & analyse', sidebarKey: 'seo' }
    },
    {
      path: '/settings',
      component: SettingsView,
      meta: { title: 'Indstillinger', sidebarKey: 'settings' }
    },
    // Fase 3 stubs
    {
      path: '/oversigt',
      component: StubView,
      meta: { title: 'Oversigt', heading: 'Oversigt', icon: 'Dashboard', sidebarKey: 'oversigt' }
    },
    {
      path: '/bookinger',
      component: StubView,
      meta: { title: 'Bookinger', heading: 'Bookinger', icon: 'Calendar', sidebarKey: 'bookinger' }
    },
    {
      path: '/statistik',
      component: StubView,
      meta: { title: 'Statistik', heading: 'Bookingstatistik', icon: 'Chart', sidebarKey: 'statistik' }
    },
    {
      path: '/behandlinger',
      component: StubView,
      meta: { title: 'Behandlinger', heading: 'Behandlinger', icon: 'Scissors', sidebarKey: 'behandlinger' }
    },
  ]
})
```

---

## API-typer (Zod-skemaer)

```typescript
// src/api/schemas.ts
import { z } from 'zod'

export const CrawlPageSchema = z.object({
  url: z.string(),
  status_code: z.number(),
  depth: z.number(),
  is_orphan: z.boolean(),
  title: z.string().nullable(),
  word_count: z.number(),
})

export const CrawlLinkSchema = z.object({
  source_url: z.string(),
  target_url: z.string(),
})

export const CrawlerStatusSchema = z.object({
  running: z.boolean(),
  page_count: z.number(),
  log_tail: z.array(z.string()),
})

export const AppSettingsSchema = z.object({
  site_url: z.string(),
  max_depth: z.number(),
  port: z.number(),
})

export type CrawlPage = z.infer<typeof CrawlPageSchema>
export type CrawlLink = z.infer<typeof CrawlLinkSchema>
export type CrawlerStatus = z.infer<typeof CrawlerStatusSchema>
export type AppSettings = z.infer<typeof AppSettingsSchema>
```

---

## Tailwind-konfiguration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
} satisfies Config
```

**Google Fonts i `index.html`:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

## FastAPI-endpoints der kræves af designet

Disse endpoints skal implementeres i backend for at designet virker:

| Endpoint | Metode | Beskrivelse |
|---|---|---|
| `/api/crawler/start` | POST | Body: `{ url, depth }`. Starter crawl. |
| `/api/crawler/stop` | POST | Stopper aktiv crawl. |
| `/api/crawler/status` | GET | Returns `{ running, page_count, log_tail }` |
| `/api/crawler/results` | GET | Returns `{ pages: [...], links: [...] }` |
| `/api/crawler/export/inventory` | GET | CSV-fil download |
| `/api/crawler/export/matrix` | GET | CSV-fil download |
| `/api/crawler/export/todo` | GET | CSV-fil download |
| `/api/crawler/graph` | GET | Serverer genereret `graph.html` |
| `/api/crawler/hierarchy` | GET | Serverer genereret `hierarchy.html` |
| `/api/settings` | GET | Returns `AppSettings` |
| `/api/settings` | PUT | Gemmer indstillinger |
| `/api/health` | GET | Returns `{ status: "ok" }` |

---

## Implementeringsrækkefølge

```
1.  Devcontainer-opdatering (Python 3.13, ports, volumes)
2.  pyproject.toml, .python-version, .gitignore, CLAUDE.md
3.  backend/config.py + database.py
4.  scrapy_crawler/ (migration)
5.  backend/crawler/ (migration + router)
6.  backend/app.py + main.py
7.  ── Backend kørende og testbar ──
8.  frontend/ vite-init + package.json + Tailwind + fonts
9.  src/api/client.ts + schemas.ts
10. src/stores/settings.ts + crawler.ts
11. src/router/index.ts
12. src/components/layout/AppSidebar.vue (inkl. AppIcon.vue)
13. src/layouts/AppLayout.vue
14. src/components/seo/StatusBadge.vue + ProblemTag.vue
15. src/components/seo/SeoControlBar.vue
16. src/components/seo/StatusStrip.vue
17. src/components/seo/PagesTable.vue
18. src/components/seo/StatsTable.vue
19. src/components/seo/HierarchyTable.vue
20. src/components/seo/ExportFooter.vue
21. src/components/seo/SeoTabs.vue
22. src/views/SeoView.vue
23. src/views/SettingsView.vue
24. src/views/StubView.vue
25. ── Hel app kørende og testbar ──
```

---

## Komponenter der ikke kræver ekstra biblioteker

Alt i designet er rent Tailwind CSS + inline SVG-ikoner. Der kræves **ingen** ekstra komponentbibliotek (ikke shadcn-vue) til Fase 2 — designet er self-contained. shadcn-vue kan tilføjes til Fase 3 hvis ønsket.

---

## CSS-animation (til StatusStrip)

Tilføjes i `src/style.css`:

```css
@import 'tailwindcss';

@keyframes kp-indeterminate {
  0%   { left: -40%; width: 40%; }
  60%  { left: 100%; width: 40%; }
  100% { left: 100%; width: 40%; }
}
.kp-indeterminate {
  animation: kp-indeterminate 1.4s ease infinite;
}
```
