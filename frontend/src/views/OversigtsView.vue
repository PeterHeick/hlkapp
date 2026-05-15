<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStatistikStore } from '@/stores/statistik'
import AppIcon from '@/components/layout/AppIcon.vue'

const stat = useStatistikStore()
onMounted(() => stat.loadPrices())

const downloading = ref(false)

function downloadBehandlinger() {
  const a = document.createElement('a')
  a.href = `/api/stats/export/behandlinger?start=${stat.dateFrom}&end=${stat.dateTo}`
  a.download = 'behandlinger.csv'
  a.click()
  downloading.value = true
  setTimeout(() => { downloading.value = false }, 2000)
}

const activeTab = ref<'omsaetning' | 'kvadranter'>('omsaetning')
const tabs = [
  { key: 'omsaetning' as const, label: 'Omsætning' },
  { key: 'kvadranter' as const, label: 'Kvadranter' },
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

const hoveredItem = ref<PlotItem | null>(null)
const useLogScale = ref(false)
const zoomLevel   = ref(1)

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

  const medCount     = sortedCounts[Math.floor(sortedCounts.length / 2)]
  const medPrice     = sortedPrices.length > 0 ? sortedPrices[Math.floor(sortedPrices.length / 2)] : 1000
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

  return { plotItems, xMid, yMid, medCount, medPrice, visMaxCount, visMaxPrice, scaleX, scaleY, uniqueYTicks, xTicks, hiddenCount }
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

      <!-- Tab-panel -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div class="flex items-center border-b border-slate-200">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
            class="px-5 py-3 text-[13px] font-medium transition-colors border-b-2"
            :class="activeTab === tab.key
              ? 'text-indigo-600 border-indigo-500 bg-indigo-50/50'
              : 'text-slate-500 border-transparent hover:text-slate-700 hover:bg-slate-50'">
            {{ tab.label }}
          </button>
          <div class="ml-auto px-3">
            <button @click="downloadBehandlinger()" :disabled="!stat.treatments || downloading"
              class="h-7 px-3 inline-flex items-center gap-1.5 rounded border transition-colors
                     text-[12px] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              :class="downloading
                ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
                : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50'">
              <AppIcon :name="downloading ? 'Check' : 'Download'" :size="12" />
              {{ downloading ? 'Hentet' : 'Hent CSV' }}
            </button>
          </div>
        </div>

        <!-- Omsætning -->
        <div v-if="activeTab === 'omsaetning'" class="p-5">
          <p v-if="!stat.revenue" class="text-[12.5px] text-slate-400 text-center py-8">
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
              <div v-for="(amount, name) in stat.revenue.by_service" :key="name"
                class="flex justify-between text-[12px] py-0.5 border-b border-slate-50">
                <span class="text-slate-600 truncate">{{ name }}</span>
                <span class="tabular-nums text-slate-800 ml-4 shrink-0">
                  {{ amount.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr
                </span>
              </div>
            </div>
          </template>
        </div>

        <!-- Kvadranter -->
        <div v-if="activeTab === 'kvadranter'" class="p-5">
          <p v-if="!quadrantData" class="text-[12.5px] text-slate-400 text-center py-8">
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <div class="grid grid-cols-2 gap-x-6 gap-y-1 mb-3 text-[11.5px]">
              <div class="flex items-start gap-2"><span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#059669"></span><span><b class="text-slate-800">Stjernerne</b> <span class="text-slate-500">— høj pris, mange behandlinger</span></span></div>
              <div class="flex items-start gap-2"><span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#7c3aed"></span><span><b class="text-slate-800">Specialiteterne</b> <span class="text-slate-500">— høj pris, få behandlinger</span></span></div>
              <div class="flex items-start gap-2"><span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#2563eb"></span><span><b class="text-slate-800">Arbejdshestene</b> <span class="text-slate-500">— lav pris, mange behandlinger</span></span></div>
              <div class="flex items-start gap-2"><span class="mt-0.5 w-2.5 h-2.5 rounded-full shrink-0" style="background:#ea580c"></span><span><b class="text-slate-800">Tidsrøverne</b> <span class="text-slate-500">— lav pris, få behandlinger</span></span></div>
            </div>
            <div class="flex items-center gap-3 mb-2 flex-wrap">
              <button @click="useLogScale = !useLogScale"
                class="h-7 px-3 rounded text-[11.5px] font-medium transition-colors"
                :class="useLogScale ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'">
                Log-skala
              </button>
              <div class="flex items-center gap-1">
                <span class="text-[11.5px] text-slate-500 mr-1">Zoom:</span>
                <button v-for="z in [1, 2, 4, 8]" :key="z" @click="zoomLevel = z; hoveredItem = null"
                  class="h-7 w-9 rounded text-[11.5px] font-medium transition-colors"
                  :class="zoomLevel === z ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'">
                  {{ z }}×
                </button>
              </div>
              <span v-if="quadrantData.hiddenCount > 0" class="text-[11px] text-slate-400 italic">
                {{ quadrantData.hiddenCount }} behandlinger er uden for visning
              </span>
            </div>
            <svg :viewBox="`0 0 ${CW} ${CH}`" class="w-full rounded-lg border border-slate-200"
              style="max-height: 440px" @mouseleave="hoveredItem = null">
              <rect :x="PL" :y="PT" :width="quadrantData.xMid - PL" :height="quadrantData.yMid - PT" fill="#f5f3ff" />
              <rect :x="quadrantData.xMid" :y="PT" :width="PL + PW - quadrantData.xMid" :height="quadrantData.yMid - PT" fill="#f0fdf4" />
              <rect :x="PL" :y="quadrantData.yMid" :width="quadrantData.xMid - PL" :height="PT + PH - quadrantData.yMid" fill="#fff7ed" />
              <rect :x="quadrantData.xMid" :y="quadrantData.yMid" :width="PL + PW - quadrantData.xMid" :height="PT + PH - quadrantData.yMid" fill="#eff6ff" />
              <line :x1="PL" :y1="PT" :x2="PL" :y2="PT + PH" stroke="#94a3b8" stroke-width="1" />
              <line :x1="PL" :y1="PT + PH" :x2="PL + PW" :y2="PT + PH" stroke="#94a3b8" stroke-width="1" />
              <line :x1="quadrantData.xMid" :y1="PT" :x2="quadrantData.xMid" :y2="PT + PH" stroke="#94a3b8" stroke-width="1" stroke-dasharray="5 3" />
              <line :x1="PL" :y1="quadrantData.yMid" :x2="PL + PW" :y2="quadrantData.yMid" stroke="#94a3b8" stroke-width="1" stroke-dasharray="5 3" />
              <text :x="PL + 7" :y="PT + 16" font-size="11" font-weight="600" fill="#7c3aed">Specialiteterne</text>
              <text :x="quadrantData.xMid + 7" :y="PT + 16" font-size="11" font-weight="600" fill="#059669">Stjernerne</text>
              <text :x="PL + 7" :y="PT + PH - 8" font-size="11" font-weight="600" fill="#ea580c">Tidsrøverne</text>
              <text :x="quadrantData.xMid + 7" :y="PT + PH - 8" font-size="11" font-weight="600" fill="#2563eb">Arbejdshestene</text>
              <g v-for="v in quadrantData.uniqueYTicks" :key="v">
                <line :x1="PL - 4" :y1="quadrantData.scaleY(v)" :x2="PL" :y2="quadrantData.scaleY(v)" stroke="#94a3b8" stroke-width="1" />
                <text :x="PL - 7" :y="quadrantData.scaleY(v) + 4" font-size="9" fill="#94a3b8" text-anchor="end">{{ v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v }}</text>
              </g>
              <g v-for="v in quadrantData.xTicks" :key="v">
                <line :x1="quadrantData.scaleX(v)" :y1="PT + PH" :x2="quadrantData.scaleX(v)" :y2="PT + PH + 4" stroke="#94a3b8" stroke-width="1" />
                <text :x="quadrantData.scaleX(v)" :y="PT + PH + 16" font-size="9" fill="#94a3b8" text-anchor="middle">{{ v }}</text>
              </g>
              <text :x="PL + PW / 2" :y="CH - 4" font-size="11" fill="#64748b" text-anchor="middle">Antal behandlinger</text>
              <text :x="14" :y="PT + PH / 2" font-size="11" fill="#64748b" text-anchor="middle" :transform="`rotate(-90 14 ${PT + PH / 2})`">Pris (kr)</text>
              <g v-for="item in quadrantData.plotItems" :key="item.service_name" class="cursor-pointer" @mouseenter="hoveredItem = item">
                <circle :cx="item.cx" :cy="item.cy" :r="item === hoveredItem ? 8 : 6"
                  :fill="qColors[item.quadrant]" :fill-opacity="item === hoveredItem ? 1 : 0.75"
                  stroke="white" stroke-width="1.5" />
                <title>{{ item.service_name }}</title>
              </g>
            </svg>
            <div class="mt-2 h-10 flex items-center gap-4 px-3 rounded-md text-[12.5px] transition-all"
              :class="hoveredItem ? 'bg-slate-50 border border-slate-200' : 'border border-transparent'">
              <template v-if="hoveredItem">
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ background: qColors[hoveredItem.quadrant] }"></span>
                <span class="font-semibold text-slate-800">{{ hoveredItem.service_name }}</span>
                <span class="text-slate-500">{{ hoveredItem.booking_count }} behandlinger</span>
                <span class="text-slate-500">{{ hoveredItem.unit_price > 0 ? hoveredItem.unit_price.toLocaleString('da-DK', { maximumFractionDigits: 0 }) + ' kr/stk' : 'ingen pris' }}</span>
                <span class="text-slate-500">{{ hoveredItem.total_revenue.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr total</span>
              </template>
              <span v-else class="text-slate-400 italic">Hold musen over en prik for at se detaljer</span>
            </div>
            <div class="mt-2 grid grid-cols-4 gap-2 text-[11.5px]">
              <div v-for="[q, label] in [['stjerne','Stjernerne'],['speciale','Specialiteterne'],['hest','Arbejdshestene'],['tidsrover','Tidsrøverne']] as [string, string][]"
                :key="q" class="rounded-md px-3 py-2 text-center" :style="{ background: qBg[q] }">
                <div class="font-semibold" :style="{ color: qColors[q] }">{{ quadrantData.plotItems.filter(i => i.quadrant === q).length }}</div>
                <div class="text-slate-500 mt-0.5">{{ label }}</div>
              </div>
            </div>
          </template>
        </div>
      </div>

    </div>
  </div>
</template>
