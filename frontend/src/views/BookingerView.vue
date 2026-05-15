<script setup lang="ts">
import { ref, computed } from 'vue'
import { useStatistikStore } from '@/stores/statistik'
import AppIcon from '@/components/layout/AppIcon.vue'

const stat = useStatistikStore()

const downloading = ref(false)

function downloadBehandleroversigt() {
  const a = document.createElement('a')
  a.href = `/api/stats/export/behandleroversigt?start=${stat.dateFrom}&end=${stat.dateTo}`
  a.download = 'behandleroversigt.csv'
  a.click()
  downloading.value = true
  setTimeout(() => { downloading.value = false }, 2000)
}

// --- Behandler-søjlediagram ---
const PALETTE = ['#6366f1','#ec4899','#f59e0b','#10b981','#3b82f6','#8b5cf6','#ef4444','#14b8a6']

const effektivitetData = computed(() => {
  const data = stat.providersBreakdown
  if (!data || data.providers.length === 0) return null

  const totalByTreatment: Record<string, number> = {}
  for (const p of data.providers)
    for (const t of p.treatments)
      totalByTreatment[t.service_name] = (totalByTreatment[t.service_name] ?? 0) + t.revenue

  const top8 = Object.entries(totalByTreatment).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([n]) => n)
  const colorMap: Record<string, string> = Object.fromEntries(top8.map((n, i) => [n, PALETTE[i]]))

  const ECW = 680, ECH = 360, EPL = 72, EPR = 20, EPT = 24, EPB = 72
  const EPW = ECW - EPL - EPR, EPH = ECH - EPT - EPB
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
      const y = yBottom - h; yBottom = y
      return { ...s, y, h }
    })
    const avgKr = p.total_count > 0 ? Math.round(p.total_revenue / p.total_count) : 0
    return { name: p.calendar_name, total: p.total_revenue, count: p.total_count, avgKr, x, w: barW, segs }
  })

  const step = maxRevenue <= 200000 ? 50000 : maxRevenue <= 500000 ? 100000 : 200000
  const yTicks = Array.from({ length: Math.ceil(maxRevenue / step) + 1 }, (_, i) => i * step)
    .filter(v => v <= maxRevenue * 1.05)
  const legend = [...top8.map((name, i) => ({ name, color: PALETTE[i] })), { name: 'Andre', color: '#94a3b8' }]

  return { bars, scaleY, yTicks, legend, ECW, ECH, EPL, EPT, EPH, EPW }
})

// --- Tidslinje + heatmap ---
const DA_MONTHS = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec']
const DA_DAYS   = ['Man','Tir','Ons','Tor','Fre','Lør','Søn']

function parseDay(iso: string) {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d)
}

type VolPoint = { x: number; y: number; date: string; count: number; dayOfWeek: number }
const hoveredVolPoint = ref<VolPoint | null>(null)

const volumeChart = computed(() => {
  const bookings = stat.volume?.bookings
  if (!bookings || bookings.length < 2) return null

  const VW = 780, VH = 190, VPL = 38, VPR = 12, VPT = 14, VPB = 54
  const VPW = VW - VPL - VPR, VPH = VH - VPT - VPB
  const maxCount = Math.max(...bookings.map(b => b.count), 1)
  const n = bookings.length

  const scaleX = (i: number) => VPL + (i / (n - 1)) * VPW
  const scaleY = (c: number) => VPT + VPH - (c / maxCount) * VPH

  const points: VolPoint[] = bookings.map((b, i) => ({
    x: scaleX(i), y: scaleY(b.count),
    date: b.date, count: b.count,
    dayOfWeek: parseDay(b.date).getDay(),
  }))

  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const areaPath = `M${points[0].x.toFixed(1)},${(VPT + VPH).toFixed(1)} ` +
    points.map(p => `L${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') +
    ` L${points[n-1].x.toFixed(1)},${(VPT + VPH).toFixed(1)} Z`

  type Shade = { x: number; w: number }
  const weekendShades: Shade[] = []
  for (let i = 0; i < points.length; i++) {
    if (points[i].dayOfWeek === 6) {
      const x1 = points[i].x
      const x2 = i + 1 < points.length ? points[i + 1].x : x1 + VPW / (n - 1)
      weekendShades.push({ x: x1, w: x2 - x1 + (i + 2 < points.length ? points[i + 2].x - x2 : 0) })
    }
  }

  const weekLines = points.filter(p => p.dayOfWeek === 1).map(p => p.x)

  type MonthLabel = { x: number; label: string }
  const monthLabels: MonthLabel[] = []
  let lastMonth = -1
  for (let i = 0; i < bookings.length; i++) {
    const d = parseDay(bookings[i].date)
    if (d.getMonth() !== lastMonth) {
      lastMonth = d.getMonth()
      monthLabels.push({ x: scaleX(i), label: `${DA_MONTHS[d.getMonth()]} ${d.getFullYear()}` })
    }
  }

  const yTicks = maxCount <= 5
    ? Array.from({ length: maxCount + 1 }, (_, i) => i)
    : [0, Math.round(maxCount / 2), maxCount]

  return { points, linePath, areaPath, weekendShades, weekLines, monthLabels, yTicks, scaleY, VW, VH, VPL, VPT, VPH, VPW }
})

// --- Ugedag-heatmap ---
type HeatCell = { iso: string; count: number; inRange: boolean }
type HeatWeek = { mondayLabel: string; days: HeatCell[] }
const hoveredCell = ref<(HeatCell & { dayName: string }) | null>(null)

function heatColor(count: number, max: number): string {
  if (count === 0) return '#f1f5f9'
  const t = Math.sqrt(count / max) // sqrt for bedre kontrast ved lave tal
  const r = Math.round(224 + (67 - 224) * t)
  const g = Math.round(231 + (56 - 231) * t)
  const b = Math.round(255 + (202 - 255) * t)
  return `rgb(${r},${g},${b})`
}

const heatmapData = computed(() => {
  const bookings = stat.volume?.bookings
  if (!bookings || bookings.length === 0) return null

  const countByDate: Record<string, number> = {}
  for (const b of bookings) countByDate[b.date] = b.count

  const maxCount = Math.max(...bookings.map(b => b.count), 1)

  // Find mandag før eller lig med første dato
  const firstDate = parseDay(bookings[0].date)
  const dow = firstDate.getDay()
  const daysToMonday = dow === 0 ? 6 : dow - 1
  const monday = new Date(firstDate)
  monday.setDate(monday.getDate() - daysToMonday)

  const lastDate = parseDay(bookings[bookings.length - 1].date)

  const weeks: HeatWeek[] = []
  const cur = new Date(monday)

  while (cur <= lastDate) {
    const days: HeatCell[] = []
    const monLabel = `${String(cur.getDate()).padStart(2,'0')}/${String(cur.getMonth()+1).padStart(2,'0')}`
    for (let d = 0; d < 7; d++) {
      const iso = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2,'0')}-${String(cur.getDate()).padStart(2,'0')}`
      days.push({ iso, count: countByDate[iso] ?? 0, inRange: iso in countByDate })
      cur.setDate(cur.getDate() + 1)
    }
    weeks.push({ mondayLabel: monLabel, days })
  }

  // Totaler pr. ugedag (kun dage i dataintervallet)
  const totals = Array(7).fill(0)
  const dayCounts = Array(7).fill(0)
  for (const w of weeks) {
    w.days.forEach((d, i) => { if (d.inRange) { totals[i] += d.count; dayCounts[i]++ } })
  }
  const dayAverages = totals.map((t, i) => dayCounts[i] > 0 ? Math.round(t / dayCounts[i] * 10) / 10 : 0)

  return { weeks, maxCount, dayAverages }
})
</script>

<template>
  <div class="flex-1 overflow-auto px-6 py-6 bg-slate-50">
    <div class="max-w-[860px] mx-auto space-y-4">

      <!-- Periode + hent-knap -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2">
          <label class="text-[12.5px] font-medium text-slate-700">Fra</label>
          <input v-model="stat.displayFrom" type="text" placeholder="dd/mm/åååå" maxlength="10"
            class="h-8 w-32 px-2 rounded-md bg-white border border-slate-300 text-[12.5px] text-slate-800
                   focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-[12.5px] font-medium text-slate-700">Til</label>
          <input v-model="stat.displayTo" type="text" placeholder="dd/mm/åååå" maxlength="10"
            class="h-8 w-32 px-2 rounded-md bg-white border border-slate-300 text-[12.5px] text-slate-800
                   focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400" />
        </div>
        <button @click="stat.loadAll()" :disabled="stat.loading"
          class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md bg-indigo-600 hover:bg-indigo-700
                 text-white text-[12.5px] font-semibold shadow-sm transition-colors
                 disabled:opacity-50 disabled:cursor-not-allowed">
          <AppIcon name="Search" :size="13" />
          {{ stat.loading ? 'Henter...' : 'Hent statistik' }}
        </button>
        <div v-if="stat.volume" class="text-[12px] text-slate-500">
          {{ stat.volume.total }} bookinger
        </div>
      </div>

      <!-- Fejlbesked -->
      <div v-if="stat.error"
        class="rounded-md bg-rose-50 border border-rose-200 px-4 py-3 text-[12.5px] text-rose-700">
        {{ stat.error }}
      </div>

      <!-- Tidslinje -->
      <div v-if="volumeChart" class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-[13px] font-semibold text-slate-800">Bookingvolumen over tid</h2>
          <div v-if="hoveredVolPoint" class="text-[12px] text-slate-600 tabular-nums">
            {{ hoveredVolPoint.date.split('-').reverse().join('/') }}
            &nbsp;·&nbsp;
            <span class="font-semibold text-slate-800">{{ hoveredVolPoint.count }} bookinger</span>
          </div>
          <span v-else class="text-[11.5px] text-slate-400 italic">Hold musen over grafen</span>
        </div>
        <div class="p-4" @mouseleave="hoveredVolPoint = null">
          <svg :viewBox="`0 0 ${volumeChart.VW} ${volumeChart.VH}`" class="w-full" style="max-height: 200px">
            <rect v-for="(s, i) in volumeChart.weekendShades" :key="i"
              :x="s.x" :y="volumeChart.VPT" :width="s.w" :height="volumeChart.VPH" fill="#f8fafc" />
            <line v-for="x in volumeChart.weekLines" :key="x"
              :x1="x" :y1="volumeChart.VPT" :x2="x" :y2="volumeChart.VPT + volumeChart.VPH"
              stroke="#e2e8f0" stroke-width="1" />
            <g v-for="v in volumeChart.yTicks" :key="v">
              <line :x1="volumeChart.VPL - 3" :y1="volumeChart.scaleY(v)"
                :x2="volumeChart.VPL + volumeChart.VPW" :y2="volumeChart.scaleY(v)" stroke="#f1f5f9" stroke-width="1" />
              <line :x1="volumeChart.VPL - 3" :y1="volumeChart.scaleY(v)"
                :x2="volumeChart.VPL" :y2="volumeChart.scaleY(v)" stroke="#cbd5e1" stroke-width="1" />
              <text :x="volumeChart.VPL - 6" :y="volumeChart.scaleY(v) + 4"
                font-size="9" fill="#94a3b8" text-anchor="end">{{ v }}</text>
            </g>
            <path :d="volumeChart.areaPath" fill="#6366f1" fill-opacity="0.08" />
            <path :d="volumeChart.linePath" fill="none" stroke="#6366f1" stroke-width="1.8"
              stroke-linejoin="round" stroke-linecap="round" />
            <circle v-if="hoveredVolPoint"
              :cx="hoveredVolPoint.x" :cy="hoveredVolPoint.y" r="4"
              fill="#6366f1" stroke="white" stroke-width="2" />
            <rect v-for="(p, i) in volumeChart.points" :key="p.date"
              :x="i === 0 ? p.x : (p.x + volumeChart.points[i-1].x) / 2"
              :y="volumeChart.VPT"
              :width="i === 0 ? (volumeChart.points[1].x - p.x) / 2
                : i === volumeChart.points.length - 1 ? (p.x - volumeChart.points[i-1].x) / 2
                : (volumeChart.points[Math.min(i+1, volumeChart.points.length-1)].x - volumeChart.points[i-1].x) / 2"
              :height="volumeChart.VPH" fill="transparent" class="cursor-crosshair"
              @mouseenter="hoveredVolPoint = p" />
            <line :x1="volumeChart.VPL" :y1="volumeChart.VPT + volumeChart.VPH"
              :x2="volumeChart.VPL + volumeChart.VPW" :y2="volumeChart.VPT + volumeChart.VPH"
              stroke="#cbd5e1" stroke-width="1" />
            <g v-for="ml in volumeChart.monthLabels" :key="ml.label">
              <line :x1="ml.x" :y1="volumeChart.VPT + volumeChart.VPH"
                :x2="ml.x" :y2="volumeChart.VPT + volumeChart.VPH + 6" stroke="#94a3b8" stroke-width="1" />
              <text :x="ml.x + 4" :y="volumeChart.VPT + volumeChart.VPH + 18"
                font-size="10" fill="#64748b" font-weight="500">{{ ml.label }}</text>
            </g>
            <line v-for="x in volumeChart.weekLines" :key="`t${x}`"
              :x1="x" :y1="volumeChart.VPT + volumeChart.VPH"
              :x2="x" :y2="volumeChart.VPT + volumeChart.VPH + 4" stroke="#cbd5e1" stroke-width="1" />
          </svg>
        </div>
      </div>

      <!-- Ugedag-heatmap -->
      <div v-if="heatmapData" class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-[13px] font-semibold text-slate-800">Travleste ugedage</h2>
          <div v-if="hoveredCell" class="text-[12px] text-slate-600">
            {{ hoveredCell.dayName }}
            <span class="text-slate-400 mx-1">·</span>
            {{ hoveredCell.iso.split('-').reverse().join('/') }}
            <span class="text-slate-400 mx-1">·</span>
            <span class="font-semibold text-slate-800">{{ hoveredCell.count }} bookinger</span>
          </div>
          <span v-else class="text-[11.5px] text-slate-400 italic">Hold musen over en dag</span>
        </div>
        <div class="p-4" @mouseleave="hoveredCell = null">
          <!-- Heatmap-gitter -->
          <div class="overflow-x-auto">
            <div class="flex gap-0.5 min-w-0" style="min-width: max-content">
              <!-- Ugedag-labels -->
              <div class="flex flex-col gap-0.5 mr-1 shrink-0">
                <div class="h-5"></div><!-- tomt felt over dag-labels (ugenr-række) -->
                <div v-for="day in DA_DAYS" :key="day"
                  class="h-5 flex items-center text-[10px] text-slate-400 font-medium w-7 justify-end pr-1">
                  {{ day }}
                </div>
              </div>
              <!-- Uge-kolonner -->
              <div v-for="week in heatmapData.weeks" :key="week.mondayLabel" class="flex flex-col gap-0.5">
                <!-- Ugestart-label -->
                <div class="h-5 flex items-end pb-0.5">
                  <span class="text-[8px] text-slate-400 leading-none">{{ week.mondayLabel }}</span>
                </div>
                <!-- Dag-celler -->
                <div
                  v-for="(cell, di) in week.days"
                  :key="cell.iso"
                  class="w-5 h-5 rounded-sm cursor-default transition-all"
                  :style="{ background: cell.inRange ? heatColor(cell.count, heatmapData.maxCount) : '#f8fafc' }"
                  :class="hoveredCell?.iso === cell.iso ? 'ring-1 ring-indigo-400' : ''"
                  @mouseenter="hoveredCell = cell.inRange ? { ...cell, dayName: DA_DAYS[di] } : null"
                />
              </div>
            </div>
          </div>

          <!-- Ugedag-gennemsnit -->
          <div class="mt-4 pt-3 border-t border-slate-100">
            <p class="text-[11px] text-slate-400 mb-2">Gennemsnit pr. ugedag</p>
            <div class="flex gap-2">
              <div
                v-for="(avg, i) in heatmapData.dayAverages"
                :key="DA_DAYS[i]"
                class="flex-1 flex flex-col items-center gap-1"
              >
                <div class="w-full rounded-sm"
                  :style="{
                    height: `${Math.max(4, avg / Math.max(...heatmapData.dayAverages) * 40)}px`,
                    background: heatColor(avg, Math.max(...heatmapData.dayAverages))
                  }"
                />
                <span class="text-[9px] text-slate-500">{{ DA_DAYS[i] }}</span>
                <span class="text-[9px] text-slate-400 tabular-nums">{{ avg }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Behandleroversigt -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-100 flex items-start justify-between gap-3">
          <div>
            <h2 class="text-[13px] font-semibold text-slate-800">Behandleroversigt</h2>
            <p class="text-[11.5px] text-slate-500 mt-0.5">
              Omsætning pr. behandler fordelt på behandlingstyper. Sammenlign farveprofiler for at se om forskellen skyldes mix eller volumen.
            </p>
          </div>
          <button @click="downloadBehandleroversigt()" :disabled="!stat.providersBreakdown || downloading"
            class="shrink-0 h-8 px-3 inline-flex items-center gap-1.5 rounded-md border transition-colors
                   text-[12px] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            :class="downloading
              ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
              : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'">
            <AppIcon :name="downloading ? 'Check' : 'Download'" :size="12" />
            {{ downloading ? 'Hentet' : 'Hent CSV' }}
          </button>
        </div>
        <div class="p-5">
          <p v-if="!effektivitetData" class="text-[12.5px] text-slate-400 text-center py-8">
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <svg :viewBox="`0 0 ${effektivitetData.ECW} ${effektivitetData.ECH}`"
              class="w-full border border-slate-200 rounded-lg" style="max-height: 380px">
              <g v-for="v in effektivitetData.yTicks" :key="v">
                <line :x1="effektivitetData.EPL - 4" :y1="effektivitetData.scaleY(v)"
                  :x2="effektivitetData.EPL + effektivitetData.EPW" :y2="effektivitetData.scaleY(v)"
                  stroke="#f1f5f9" stroke-width="1" />
                <line :x1="effektivitetData.EPL - 4" :y1="effektivitetData.scaleY(v)"
                  :x2="effektivitetData.EPL" :y2="effektivitetData.scaleY(v)" stroke="#94a3b8" stroke-width="1" />
                <text :x="effektivitetData.EPL - 7" :y="effektivitetData.scaleY(v) + 4"
                  font-size="9" fill="#94a3b8" text-anchor="end">
                  {{ v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v }}
                </text>
              </g>
              <line :x1="effektivitetData.EPL" y1="24"
                :x2="effektivitetData.EPL" :y2="24 + effektivitetData.EPH" stroke="#94a3b8" stroke-width="1" />
              <g v-for="bar in effektivitetData.bars" :key="bar.name">
                <rect v-for="seg in bar.segs" :key="seg.name"
                  :x="seg.x" :y="seg.y" :width="seg.w" :height="seg.h" :fill="seg.color" fill-opacity="0.88">
                  <title>{{ seg.name }}: {{ seg.revenue.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr</title>
                </rect>
                <text :x="bar.x + bar.w / 2" :y="effektivitetData.scaleY(bar.total) - 4"
                  font-size="9" fill="#475569" text-anchor="middle">{{ (bar.total / 1000).toFixed(0) }}k</text>
                <text :x="bar.x + bar.w / 2" :y="24 + effektivitetData.EPH + 14"
                  font-size="10" fill="#475569" text-anchor="middle">{{ bar.name.split(' ')[0] }}</text>
                <text :x="bar.x + bar.w / 2" :y="24 + effektivitetData.EPH + 26"
                  font-size="9" fill="#94a3b8" text-anchor="middle">
                  {{ bar.count }} beh · {{ bar.avgKr.toLocaleString('da-DK') }} kr/beh
                </text>
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
      </div>

    </div>
  </div>
</template>
