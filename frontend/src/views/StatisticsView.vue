<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useStatistikStore } from '@/stores/statistik'
import AppIcon from '@/components/layout/AppIcon.vue'

const stat = useStatistikStore()
onMounted(() => stat.loadPrices())

function isoToDanish(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

function formatDate(iso: string): string {
  return isoToDanish(iso)
}

function danishToIso(val: string): string | null {
  const m = val.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
  if (!m) return null
  return `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}`
}

const displayFrom = ref(isoToDanish(stat.dateFrom))
const displayTo   = ref(isoToDanish(stat.dateTo))

watch(displayFrom, (val) => { const iso = danishToIso(val); if (iso) stat.dateFrom = iso })
watch(displayTo,   (val) => { const iso = danishToIso(val); if (iso) stat.dateTo   = iso })

const activeTab = ref<'krtime' | 'behandlere' | 'omsaetning' | 'ressourcer' | 'kvadranter' | 'prisliste'>('krtime')
const sortBy = ref<'revenue' | 'count'>('revenue')

const tabs = [
  { key: 'krtime' as const,     label: 'Behandlinger' },
  { key: 'behandlere' as const, label: 'Behandlere' },
  { key: 'omsaetning' as const, label: 'Omsætning' },
  { key: 'ressourcer' as const, label: 'Ressourcer' },
  { key: 'kvadranter' as const, label: 'Kvadranter' },
  { key: 'prisliste' as const,  label: 'Prisliste' },
]

// --- Kvadrant-diagram ---
const CW = 680, CH = 420, PL = 68, PR = 24, PT = 36, PB = 52
const PW = CW - PL - PR
const PH = CH - PT - PB

type PlotItem = {
  service_name: string
  booking_count: number
  unit_price: number
  total_revenue: number
  cx: number
  cy: number
  quadrant: 'stjerne' | 'speciale' | 'hest' | 'tidsrover'
}

const hoveredItem  = ref<PlotItem | null>(null)
const useLogScale  = ref(false)
const zoomLevel    = ref(1)   // 1 = alt, 2 = halvt interval, 4 = kvart, 8 = ottendedel

const qColors: Record<string, string> = {
  stjerne:   '#059669',
  speciale:  '#7c3aed',
  hest:      '#2563eb',
  tidsrover: '#ea580c',
}
const qBg: Record<string, string> = {
  stjerne:   '#f0fdf4',
  speciale:  '#f5f3ff',
  hest:      '#eff6ff',
  tidsrover: '#fff7ed',
}

const quadrantData = computed(() => {
  const items = (stat.treatments?.items ?? []).filter(i => i.booking_count > 0)
  if (items.length < 2) return null

  const sortedCounts = items.map(i => i.booking_count).sort((a, b) => a - b)
  const withPrice    = items.filter(i => i.unit_price > 0)
  const sortedPrices = withPrice.map(i => i.unit_price).sort((a, b) => a - b)

  const medCount  = sortedCounts[Math.floor(sortedCounts.length / 2)]
  const medPrice  = sortedPrices.length > 0 ? sortedPrices[Math.floor(sortedPrices.length / 2)] : 1000
  const trueMaxCount = sortedCounts[sortedCounts.length - 1]
  const trueMaxPrice = Math.max(...items.map(i => i.unit_price), 1)

  const visMaxCount = Math.ceil(trueMaxCount / zoomLevel.value)
  const visMaxPrice = Math.ceil(trueMaxPrice / zoomLevel.value)

  const norm = (x: number, max: number) =>
    useLogScale.value
      ? (max > 1 ? Math.log(x + 1) / Math.log(max + 1) : 0)
      : (max > 0 ? x / max : 0)

  const scaleX = (n: number) => PL + norm(Math.min(n, visMaxCount), visMaxCount) * PW
  const scaleY = (p: number) => PT + PH - norm(Math.min(p, visMaxPrice), visMaxPrice) * PH

  const xMid = scaleX(medCount)
  const yMid = scaleY(medPrice)

  const visibleItems = items.filter(i => i.booking_count <= visMaxCount && i.unit_price <= visMaxPrice)
  const hiddenCount  = items.length - visibleItems.length

  const plotItems: PlotItem[] = visibleItems.map(item => {
    const q: PlotItem['quadrant'] =
      item.booking_count >= medCount && item.unit_price >= medPrice ? 'stjerne'
      : item.booking_count >= medCount                              ? 'hest'
      : item.unit_price >= medPrice                                 ? 'speciale'
      : 'tidsrover'
    return { ...item, cx: scaleX(item.booking_count), cy: scaleY(item.unit_price), quadrant: q }
  })

  const yTicks: number[] = useLogScale.value
    ? [0, 500, 1000, 2000, 5000, 10000, 15000, 20000].filter(v => v <= visMaxPrice)
    : [0, Math.round(visMaxPrice / 2), visMaxPrice]
  if (yTicks[yTicks.length - 1] !== visMaxPrice) yTicks.push(visMaxPrice)
  const uniqueYTicks = [...new Set(yTicks)]

  const xTicks = [...new Set([0, medCount, visMaxCount])]

  return {
    plotItems, xMid, yMid,
    medCount, medPrice, visMaxCount, visMaxPrice,
    scaleX, scaleY, uniqueYTicks, xTicks, hiddenCount,
  }
})

// --- Ressourcer: Bar-in-Bar ---
const ressourcerData = computed(() => {
  const items = (stat.treatments?.items ?? []).filter(i => i.booking_count > 0)
  if (items.length === 0) return null
  const totalCount   = items.reduce((s, i) => s + i.booking_count, 0)
  const totalRevenue = items.reduce((s, i) => s + i.total_revenue, 0)
  if (totalCount === 0) return null
  return items
    .map(i => ({
      name:        i.service_name,
      bookingPct:  (i.booking_count / totalCount) * 100,
      revenuePct:  totalRevenue > 0 ? (i.total_revenue / totalRevenue) * 100 : 0,
      count:       i.booking_count,
      revenue:     i.total_revenue,
    }))
    .sort((a, b) => b.revenuePct - a.revenuePct)
})

// --- Effektivitet: Stacked Bar ---
const PALETTE = ['#6366f1','#ec4899','#f59e0b','#10b981','#3b82f6','#8b5cf6','#ef4444','#14b8a6']

const effektivitetData = computed(() => {
  const data = stat.providersBreakdown
  if (!data || data.providers.length === 0) return null

  // Top 8 behandlingstyper på tværs af alle behandlere (efter omsætning)
  const totalByTreatment: Record<string, number> = {}
  for (const p of data.providers) {
    for (const t of p.treatments) {
      totalByTreatment[t.service_name] = (totalByTreatment[t.service_name] ?? 0) + t.revenue
    }
  }
  const top8 = Object.entries(totalByTreatment)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name]) => name)
  const colorMap: Record<string, string> = Object.fromEntries(top8.map((n, i) => [n, PALETTE[i]]))

  const ECW = 680, ECH = 360
  const EPL = 72, EPR = 20, EPT = 24, EPB = 72
  const EPW = ECW - EPL - EPR
  const EPH = ECH - EPT - EPB

  const n = data.providers.length
  const barW = Math.min(88, Math.floor((EPW / n) * 0.62))
  const spacing = (EPW - barW * n) / (n + 1)

  const maxRevenue = Math.max(...data.providers.map(p => p.total_revenue), 1)
  const scaleY = (r: number) => EPT + EPH - (r / maxRevenue) * EPH

  type Seg = { name: string; revenue: number; color: string; x: number; y: number; w: number; h: number }
  const bars = data.providers.map((p, i) => {
    const x = EPL + spacing + i * (barW + spacing)
    let yBottom = EPT + EPH
    const top: Seg[] = []
    let andre = 0
    for (const t of p.treatments) {
      if (colorMap[t.service_name]) top.push({ name: t.service_name, revenue: t.revenue, color: colorMap[t.service_name], x, y: 0, w: barW, h: 0 })
      else andre += t.revenue
    }
    if (andre > 0) top.push({ name: 'Andre', revenue: andre, color: '#94a3b8', x, y: 0, w: barW, h: 0 })
    top.sort((a, b) => b.revenue - a.revenue)
    const segs: Seg[] = top.map(s => {
      const h = Math.max((s.revenue / maxRevenue) * EPH, s.revenue > 0 ? 1 : 0)
      const y = yBottom - h
      yBottom = y
      return { ...s, y, h }
    })
    const avgKr = p.total_count > 0 ? Math.round(p.total_revenue / p.total_count) : 0
    return { name: p.calendar_name, total: p.total_revenue, count: p.total_count, avgKr, x, w: barW, segs }
  })

  // Y-akse ticks
  const step = maxRevenue <= 200000 ? 50000 : maxRevenue <= 500000 ? 100000 : 200000
  const yTicks = Array.from({ length: Math.ceil(maxRevenue / step) + 1 }, (_, i) => i * step)
    .filter(v => v <= maxRevenue * 1.05)

  const legend = [
    ...top8.map((name, i) => ({ name, color: PALETTE[i] })),
    { name: 'Andre', color: '#94a3b8' },
  ]

  return { bars, scaleY, yTicks, legend, ECW, ECH, EPL, EPT, EPH, EPW }
})

const sortedTreatments = computed(() => {
  const items = stat.treatments?.items ?? []
  return sortBy.value === 'revenue'
    ? [...items].sort((a, b) => b.total_revenue - a.total_revenue)
    : [...items].sort((a, b) => b.booking_count - a.booking_count)
})

const maxTreatmentValue = computed(() =>
  sortBy.value === 'revenue'
    ? Math.max(...sortedTreatments.value.map(i => i.total_revenue), 1)
    : Math.max(...sortedTreatments.value.map(i => i.booking_count), 1)
)



</script>

<template>
  <div class="flex-1 overflow-auto px-6 py-6 bg-slate-50">
    <div class="max-w-[860px] mx-auto space-y-4">

      <!-- Periode + hent-knap -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2">
          <label class="text-[12.5px] font-medium text-slate-700">Fra</label>
          <input
            v-model="displayFrom"
            type="text"
            placeholder="dd/mm/åååå"
            maxlength="10"
            class="h-8 w-32 px-2 rounded-md bg-white border border-slate-300 text-[12.5px] text-slate-800
                   focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400"
          />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-[12.5px] font-medium text-slate-700">Til</label>
          <input
            v-model="displayTo"
            type="text"
            placeholder="dd/mm/åååå"
            maxlength="10"
            class="h-8 w-32 px-2 rounded-md bg-white border border-slate-300 text-[12.5px] text-slate-800
                   focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400"
          />
        </div>
        <button
          @click="stat.loadAll()"
          :disabled="stat.loading"
          class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md bg-indigo-600 hover:bg-indigo-700
                 text-white text-[12.5px] font-semibold shadow-sm transition-colors
                 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <AppIcon name="Search" :size="13" />
          {{ stat.loading ? 'Henter...' : 'Hent statistik' }}
        </button>
        <div v-if="stat.volume" class="text-[12px] text-slate-500">
          {{ stat.volume.total }} bookinger
        </div>
      </div>

      <!-- Fejlbesked -->
      <div
        v-if="stat.error"
        class="rounded-md bg-rose-50 border border-rose-200 px-4 py-3 text-[12.5px] text-rose-700"
      >
        {{ stat.error }}
      </div>

      <!-- Tab-panel -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div class="flex border-b border-slate-200 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            class="px-5 py-3 text-[13px] font-medium transition-colors border-b-2"
            :class="activeTab === tab.key
              ? 'text-indigo-600 border-indigo-500 bg-indigo-50/50'
              : 'text-slate-500 border-transparent hover:text-slate-700 hover:bg-slate-50'"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Behandlinger -->
        <div v-if="activeTab === 'krtime'" class="p-5">
          <div v-if="stat.treatments && stat.treatments.items.length > 0" class="flex gap-2 mb-4">
            <button
              @click="sortBy = 'revenue'"
              class="h-7 px-3 rounded text-[12px] font-medium transition-colors"
              :class="sortBy === 'revenue'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            >Omsætning</button>
            <button
              @click="sortBy = 'count'"
              class="h-7 px-3 rounded text-[12px] font-medium transition-colors"
              :class="sortBy === 'count'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            >Popularitet</button>
          </div>
          <p
            v-if="!stat.treatments || stat.treatments.items.length === 0"
            class="text-[12.5px] text-slate-400 text-center py-8"
          >
            Ingen data — hent statistik for den valgte periode
          </p>
          <div v-else class="space-y-3">
            <div v-for="item in sortedTreatments" :key="item.service_name" class="space-y-1">
              <div class="flex justify-between text-[12.5px]">
                <span class="font-medium text-slate-800">{{ item.service_name }}</span>
                <span class="tabular-nums text-slate-600">
                  <template v-if="sortBy === 'revenue'">
                    {{ item.total_revenue.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr
                  </template>
                  <template v-else>
                    {{ item.booking_count }} bookinger
                  </template>
                </span>
              </div>
              <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-indigo-500 rounded-full transition-all"
                  :style="{ width: `${(sortBy === 'revenue' ? item.total_revenue : item.booking_count) / maxTreatmentValue * 100}%` }"
                />
              </div>
              <div class="text-[11px] text-slate-400">
                {{ item.booking_count }} bookinger
                <template v-if="item.unit_price > 0">
                  · {{ item.unit_price.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr/stk
                </template>
                <template v-else>
                  · pris ikke sat
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- Behandlere -->
        <div v-if="activeTab === 'behandlere'" class="p-5">
          <p v-if="!effektivitetData" class="text-[12.5px] text-slate-400 text-center py-8">
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <p class="text-[11.5px] text-slate-500 mb-3">
              Omsætning pr. behandler fordelt på behandlingstyper. Farverne viser hvilke behandlinger der driver omsætningen — sammenlign farveprofiler for at se om forskellen skyldes mix eller volumen.
            </p>
            <svg
              :viewBox="`0 0 ${effektivitetData.ECW} ${effektivitetData.ECH}`"
              class="w-full border border-slate-200 rounded-lg"
              style="max-height: 380px"
            >
              <g v-for="v in effektivitetData.yTicks" :key="v">
                <line :x1="effektivitetData.EPL - 4" :y1="effektivitetData.scaleY(v)" :x2="effektivitetData.EPL + effektivitetData.EPW" :y2="effektivitetData.scaleY(v)" stroke="#f1f5f9" stroke-width="1" />
                <line :x1="effektivitetData.EPL - 4" :y1="effektivitetData.scaleY(v)" :x2="effektivitetData.EPL" :y2="effektivitetData.scaleY(v)" stroke="#94a3b8" stroke-width="1" />
                <text :x="effektivitetData.EPL - 7" :y="effektivitetData.scaleY(v) + 4" font-size="9" fill="#94a3b8" text-anchor="end">
                  {{ v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v }}
                </text>
              </g>
              <line :x1="effektivitetData.EPL" y1="24" :x2="effektivitetData.EPL" :y2="24 + effektivitetData.EPH" stroke="#94a3b8" stroke-width="1" />
              <g v-for="bar in effektivitetData.bars" :key="bar.name">
                <rect v-for="seg in bar.segs" :key="seg.name" :x="seg.x" :y="seg.y" :width="seg.w" :height="seg.h" :fill="seg.color" fill-opacity="0.88">
                  <title>{{ seg.name }}: {{ seg.revenue.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr</title>
                </rect>
                <text :x="bar.x + bar.w / 2" :y="effektivitetData.scaleY(bar.total) - 4" font-size="9" fill="#475569" text-anchor="middle">{{ (bar.total / 1000).toFixed(0) }}k</text>
                <text :x="bar.x + bar.w / 2" :y="24 + effektivitetData.EPH + 14" font-size="10" fill="#475569" text-anchor="middle">{{ bar.name.split(' ')[0] }}</text>
                <text :x="bar.x + bar.w / 2" :y="24 + effektivitetData.EPH + 26" font-size="9" fill="#94a3b8" text-anchor="middle">{{ bar.count }} beh · {{ bar.avgKr.toLocaleString('da-DK') }} kr/beh</text>
              </g>
            </svg>
            <div class="mt-3 flex flex-wrap gap-x-4 gap-y-1">
              <div v-for="l in effektivitetData.legend" :key="l.name" class="flex items-center gap-1.5 text-[11px]">
                <span class="w-2.5 h-2.5 rounded-sm shrink-0" :style="{ background: l.color }"></span>
                <span class="text-slate-600">{{ l.name.length > 30 ? l.name.slice(0,29)+'…' : l.name }}</span>
              </div>
            </div>
          </template>
        </div>

        <!-- Omsætning -->
        <div v-if="activeTab === 'omsaetning'" class="p-5">
          <p
            v-if="!stat.revenue"
            class="text-[12.5px] text-slate-400 text-center py-8"
          >
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <div class="flex items-center justify-between mb-5 pb-4 border-b border-slate-100">
              <span class="text-[13px] font-semibold text-slate-700">Total omsætning</span>
              <span class="text-[20px] font-bold text-slate-900">
                {{ stat.revenue.total_revenue.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr
              </span>
            </div>
            <div class="grid grid-cols-2 gap-x-6 gap-y-1">
              <div
                v-for="(amount, name) in stat.revenue.by_service"
                :key="name"
                class="flex justify-between text-[12px] py-0.5 border-b border-slate-50"
              >
                <span class="text-slate-600 truncate">{{ name }}</span>
                <span class="tabular-nums text-slate-800 ml-4 shrink-0">
                  {{ amount.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr
                </span>
              </div>
            </div>
          </template>
        </div>

        <!-- Ressourcer: Bar-in-Bar -->
        <div v-if="activeTab === 'ressourcer'" class="p-5">
          <p v-if="!ressourcerData" class="text-[12.5px] text-slate-400 text-center py-8">
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <p class="text-[11.5px] text-slate-500 mb-3">
              Sammenligner hvor meget en behandling fylder i kalenderen (% af bookinger) vs. hvad den bidrager til omsætningen (% af omsætning). En behandling der fylder lidt men omsætter meget er en "vinder".
            </p>
            <!-- Legend -->
            <div class="flex gap-5 mb-3 text-[11.5px]">
              <span class="flex items-center gap-1.5"><span class="w-3 h-2.5 rounded-sm inline-block bg-blue-500"></span>% af bookinger</span>
              <span class="flex items-center gap-1.5"><span class="w-3 h-2.5 rounded-sm inline-block bg-emerald-500"></span>% af omsætning</span>
            </div>
            <!-- Scrollbar wrapper -->
            <div class="overflow-y-auto" style="max-height: 520px">
              <svg
                :width="680"
                :height="60 + ressourcerData.length * 32"
                :viewBox="`0 0 680 ${60 + ressourcerData.length * 32}`"
                class="w-full"
              >
                <!-- Grid -->
                <g v-for="pct in [25, 50, 75, 100]" :key="pct">
                  <line :x1="230 + pct * 3.9" y1="10" :x2="230 + pct * 3.9" :y2="50 + ressourcerData.length * 32" stroke="#f1f5f9" stroke-width="1" />
                  <text :x="230 + pct * 3.9" y="22" font-size="8" fill="#cbd5e1" text-anchor="middle">{{ pct }}%</text>
                </g>
                <!-- Rows -->
                <g v-for="(item, idx) in ressourcerData" :key="item.name">
                  <!-- Treatment name -->
                  <text
                    x="5"
                    :y="36 + idx * 32"
                    font-size="10"
                    fill="#475569"
                    dominant-baseline="middle"
                  >{{ item.name.length > 32 ? item.name.slice(0, 31) + '…' : item.name }}</text>
                  <!-- Booking% bar -->
                  <rect
                    x="230"
                    :y="26 + idx * 32"
                    :width="item.bookingPct * 3.9"
                    height="9"
                    rx="2"
                    fill="#3b82f6"
                    fill-opacity="0.8"
                  />
                  <!-- Revenue% bar -->
                  <rect
                    x="230"
                    :y="37 + idx * 32"
                    :width="item.revenuePct * 3.9"
                    height="9"
                    rx="2"
                    fill="#10b981"
                    fill-opacity="0.85"
                  />
                  <!-- Labels -->
                  <text :x="233 + Math.max(item.bookingPct, item.revenuePct) * 3.9" :y="36 + idx * 32" font-size="9" fill="#94a3b8" dominant-baseline="middle">
                    {{ item.bookingPct.toFixed(1) }}% / {{ item.revenuePct.toFixed(1) }}%
                  </text>
                </g>
              </svg>
            </div>
          </template>
        </div>

        <!-- Kvadranter -->
        <div v-if="activeTab === 'kvadranter'" class="p-5">
          <p
            v-if="!quadrantData"
            class="text-[12.5px] text-slate-400 text-center py-8"
          >
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <!-- Forklaring -->
            <div class="grid grid-cols-2 gap-x-6 gap-y-1 mb-3 text-[11.5px]">
              <div class="flex items-start gap-2">
                <span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#059669"></span>
                <span><b class="text-slate-800">Stjernerne</b> <span class="text-slate-500">— høj pris, mange behandlinger</span></span>
              </div>
              <div class="flex items-start gap-2">
                <span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#7c3aed"></span>
                <span><b class="text-slate-800">Specialiteterne</b> <span class="text-slate-500">— høj pris, få behandlinger</span></span>
              </div>
              <div class="flex items-start gap-2">
                <span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#2563eb"></span>
                <span><b class="text-slate-800">Arbejdshestene</b> <span class="text-slate-500">— lav pris, mange behandlinger</span></span>
              </div>
              <div class="flex items-start gap-2">
                <span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#ea580c"></span>
                <span><b class="text-slate-800">Tidsrøverne</b> <span class="text-slate-500">— lav pris, få behandlinger</span></span>
              </div>
            </div>

            <!-- Kontroller -->
            <div class="flex items-center gap-3 mb-2 flex-wrap">
              <button
                @click="useLogScale = !useLogScale"
                class="h-7 px-3 rounded text-[11.5px] font-medium transition-colors"
                :class="useLogScale
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
              >
                Log-skala
              </button>
              <div class="flex items-center gap-1">
                <span class="text-[11.5px] text-slate-500 mr-1">Zoom:</span>
                <button
                  v-for="z in [1, 2, 4, 8]"
                  :key="z"
                  @click="zoomLevel = z; hoveredItem = null"
                  class="h-7 w-9 rounded text-[11.5px] font-medium transition-colors"
                  :class="zoomLevel === z
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
                >{{ z }}×</button>
              </div>
              <span v-if="quadrantData.hiddenCount > 0" class="text-[11px] text-slate-400 italic">
                {{ quadrantData.hiddenCount }} behandlinger er uden for visning
              </span>
            </div>

            <!-- SVG-diagram -->
            <svg
              :viewBox="`0 0 ${CW} ${CH}`"
              class="w-full rounded-lg border border-slate-200"
              style="max-height: 440px"
              @mouseleave="hoveredItem = null"
            >
              <!-- Kvadrant-baggrunde -->
              <rect :x="PL" :y="PT" :width="quadrantData.xMid - PL" :height="quadrantData.yMid - PT" fill="#f5f3ff" />
              <rect :x="quadrantData.xMid" :y="PT" :width="PL + PW - quadrantData.xMid" :height="quadrantData.yMid - PT" fill="#f0fdf4" />
              <rect :x="PL" :y="quadrantData.yMid" :width="quadrantData.xMid - PL" :height="PT + PH - quadrantData.yMid" fill="#fff7ed" />
              <rect :x="quadrantData.xMid" :y="quadrantData.yMid" :width="PL + PW - quadrantData.xMid" :height="PT + PH - quadrantData.yMid" fill="#eff6ff" />

              <!-- Akser -->
              <line :x1="PL" :y1="PT" :x2="PL" :y2="PT + PH" stroke="#94a3b8" stroke-width="1" />
              <line :x1="PL" :y1="PT + PH" :x2="PL + PW" :y2="PT + PH" stroke="#94a3b8" stroke-width="1" />

              <!-- Median-linjer (stiplet) -->
              <line :x1="quadrantData.xMid" :y1="PT" :x2="quadrantData.xMid" :y2="PT + PH" stroke="#94a3b8" stroke-width="1" stroke-dasharray="5 3" />
              <line :x1="PL" :y1="quadrantData.yMid" :x2="PL + PW" :y2="quadrantData.yMid" stroke="#94a3b8" stroke-width="1" stroke-dasharray="5 3" />

              <!-- Kvadrant-etiketter -->
              <text :x="PL + 7" :y="PT + 16" font-size="11" font-weight="600" fill="#7c3aed">Specialiteterne</text>
              <text :x="quadrantData.xMid + 7" :y="PT + 16" font-size="11" font-weight="600" fill="#059669">Stjernerne</text>
              <text :x="PL + 7" :y="PT + PH - 8" font-size="11" font-weight="600" fill="#ea580c">Tidsrøverne</text>
              <text :x="quadrantData.xMid + 7" :y="PT + PH - 8" font-size="11" font-weight="600" fill="#2563eb">Arbejdshestene</text>

              <!-- Y-akse ticks -->
              <g v-for="v in quadrantData.uniqueYTicks" :key="v">
                <line :x1="PL - 4" :y1="quadrantData.scaleY(v)" :x2="PL" :y2="quadrantData.scaleY(v)" stroke="#94a3b8" stroke-width="1" />
                <text :x="PL - 7" :y="quadrantData.scaleY(v) + 4" font-size="9" fill="#94a3b8" text-anchor="end">
                  {{ v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v }}
                </text>
              </g>

              <!-- X-akse ticks -->
              <g v-for="v in quadrantData.xTicks" :key="v">
                <line :x1="quadrantData.scaleX(v)" :y1="PT + PH" :x2="quadrantData.scaleX(v)" :y2="PT + PH + 4" stroke="#94a3b8" stroke-width="1" />
                <text :x="quadrantData.scaleX(v)" :y="PT + PH + 16" font-size="9" fill="#94a3b8" text-anchor="middle">{{ v }}</text>
              </g>

              <!-- Aksetitler -->
              <text :x="PL + PW / 2" :y="CH - 4" font-size="11" fill="#64748b" text-anchor="middle">Antal behandlinger</text>
              <text
                :x="14"
                :y="PT + PH / 2"
                font-size="11"
                fill="#64748b"
                text-anchor="middle"
                :transform="`rotate(-90 14 ${PT + PH / 2})`"
              >Pris (kr)</text>

              <!-- Behandlings-prikker -->
              <g
                v-for="item in quadrantData.plotItems"
                :key="item.service_name"
                class="cursor-pointer"
                @mouseenter="hoveredItem = item"
              >
                <circle
                  :cx="item.cx"
                  :cy="item.cy"
                  :r="item === hoveredItem ? 8 : 6"
                  :fill="qColors[item.quadrant]"
                  :fill-opacity="item === hoveredItem ? 1 : 0.75"
                  stroke="white"
                  stroke-width="1.5"
                />
                <title>{{ item.service_name }}</title>
              </g>
            </svg>

            <!-- Hover-info -->
            <div
              class="mt-2 h-10 flex items-center gap-4 px-3 rounded-md text-[12.5px] transition-all"
              :class="hoveredItem ? 'bg-slate-50 border border-slate-200' : 'border border-transparent'"
            >
              <template v-if="hoveredItem">
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ background: qColors[hoveredItem.quadrant] }"></span>
                <span class="font-semibold text-slate-800">{{ hoveredItem.service_name }}</span>
                <span class="text-slate-500">{{ hoveredItem.booking_count }} behandlinger</span>
                <span class="text-slate-500">
                  {{ hoveredItem.unit_price > 0
                    ? hoveredItem.unit_price.toLocaleString('da-DK', { maximumFractionDigits: 0 }) + ' kr/stk'
                    : 'ingen pris' }}
                </span>
                <span class="text-slate-500">
                  {{ hoveredItem.total_revenue.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr total
                </span>
              </template>
              <span v-else class="text-slate-400 italic">Hold musen over en prik for at se detaljer</span>
            </div>

            <!-- Kvadrant-tælling -->
            <div class="mt-2 grid grid-cols-4 gap-2 text-[11.5px]">
              <div
                v-for="[q, label] in [['stjerne','Stjernerne'],['speciale','Specialiteterne'],['hest','Arbejdshestene'],['tidsrover','Tidsrøverne']] as [string, string][]"
                :key="q"
                class="rounded-md px-3 py-2 text-center"
                :style="{ background: qBg[q] }"
              >
                <div class="font-semibold" :style="{ color: qColors[q] }">
                  {{ quadrantData.plotItems.filter(i => i.quadrant === q).length }}
                </div>
                <div class="text-slate-500 mt-0.5">{{ label }}</div>
              </div>
            </div>
          </template>
        </div>

        <!-- Prisliste -->
        <div v-if="activeTab === 'prisliste'" class="p-5">
          <p
            v-if="Object.keys(stat.priceList).length === 0"
            class="text-[12.5px] text-slate-400 text-center py-8"
          >
            Ingen priser — kør "Opdater priser" under Indstillinger
          </p>
          <table v-else class="w-full text-[12.5px]">
            <thead>
              <tr class="border-b border-slate-200">
                <th class="text-left font-semibold text-slate-700 pb-2">Behandling</th>
                <th class="text-right font-semibold text-slate-700 pb-2">Pris</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(price, name) in stat.priceList"
                :key="name"
                class="border-b border-slate-50 hover:bg-slate-50"
              >
                <td class="py-1.5 text-slate-800">{{ name }}</td>
                <td class="py-1.5 text-right tabular-nums text-slate-700">
                  {{ price > 0
                    ? price.toLocaleString('da-DK', { maximumFractionDigits: 0 }) + ' kr'
                    : '—'
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

    </div>
  </div>
</template>
