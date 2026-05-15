<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStatistikStore } from '@/stores/statistik'
import AppIcon from '@/components/layout/AppIcon.vue'

const stat = useStatistikStore()
onMounted(() => stat.loadPrices())

const downloadingBehandlinger = ref(false)

function downloadBehandlinger() {
  const a = document.createElement('a')
  a.href = `/api/stats/export/behandlinger?start=${stat.dateFrom}&end=${stat.dateTo}`
  a.download = 'behandlinger.csv'
  a.click()
  downloadingBehandlinger.value = true
  setTimeout(() => { downloadingBehandlinger.value = false }, 2000)
}

const activeTab = ref<'krtime' | 'ressourcer'>('krtime')
const tabs = [
  { key: 'krtime' as const,     label: 'Behandlinger' },
  { key: 'ressourcer' as const, label: 'Ressourcer' },
]

const sortBy = ref<'revenue' | 'count'>('revenue')

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

const ressourcerData = computed(() => {
  const items = (stat.treatments?.items ?? []).filter(i => i.booking_count > 0)
  if (items.length === 0) return null
  const totalCount   = items.reduce((s, i) => s + i.booking_count, 0)
  const totalRevenue = items.reduce((s, i) => s + i.total_revenue, 0)
  if (totalCount === 0) return null
  return items
    .map(i => ({
      name:       i.service_name,
      bookingPct: (i.booking_count / totalCount) * 100,
      revenuePct: totalRevenue > 0 ? (i.total_revenue / totalRevenue) * 100 : 0,
      count:      i.booking_count,
      revenue:    i.total_revenue,
    }))
    .sort((a, b) => b.revenuePct - a.revenuePct)
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
            <button @click="downloadBehandlinger()" :disabled="!stat.treatments || downloadingBehandlinger"
              class="h-7 px-3 inline-flex items-center gap-1.5 rounded border transition-colors
                     text-[12px] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              :class="downloadingBehandlinger
                ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
                : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50'">
              <AppIcon :name="downloadingBehandlinger ? 'Check' : 'Download'" :size="12" />
              {{ downloadingBehandlinger ? 'Hentet' : 'Hent CSV' }}
            </button>
          </div>
        </div>

        <!-- Behandlinger -->
        <div v-if="activeTab === 'krtime'" class="p-5">
          <div v-if="stat.treatments && stat.treatments.items.length > 0" class="flex gap-2 mb-4">
            <button @click="sortBy = 'revenue'"
              class="h-7 px-3 rounded text-[12px] font-medium transition-colors"
              :class="sortBy === 'revenue' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'">
              Omsætning
            </button>
            <button @click="sortBy = 'count'"
              class="h-7 px-3 rounded text-[12px] font-medium transition-colors"
              :class="sortBy === 'count' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'">
              Popularitet
            </button>
          </div>
          <p v-if="!stat.treatments || stat.treatments.items.length === 0"
            class="text-[12.5px] text-slate-400 text-center py-8">
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
                  <template v-else>{{ item.booking_count }} bookinger</template>
                </span>
              </div>
              <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div class="h-full bg-indigo-500 rounded-full transition-all"
                  :style="{ width: `${(sortBy === 'revenue' ? item.total_revenue : item.booking_count) / maxTreatmentValue * 100}%` }" />
              </div>
              <div class="text-[11px] text-slate-400">
                {{ item.booking_count }} bookinger
                <template v-if="item.unit_price > 0">
                  · {{ item.unit_price.toLocaleString('da-DK', { maximumFractionDigits: 0 }) }} kr/stk
                </template>
                <template v-else>· pris ikke sat</template>
              </div>
            </div>
          </div>
        </div>

        <!-- Ressourcer -->
        <div v-if="activeTab === 'ressourcer'" class="p-5">
          <p v-if="!ressourcerData" class="text-[12.5px] text-slate-400 text-center py-8">
            Ingen data — hent statistik for den valgte periode
          </p>
          <template v-else>
            <p class="text-[11.5px] text-slate-500 mb-3">
              Sammenligner hvor meget en behandling fylder i kalenderen (% af bookinger) vs. hvad den bidrager til omsætningen (% af omsætning).
            </p>
            <div class="flex gap-5 mb-3 text-[11.5px]">
              <span class="flex items-center gap-1.5"><span class="w-3 h-2.5 rounded-sm inline-block bg-blue-500"></span>% af bookinger</span>
              <span class="flex items-center gap-1.5"><span class="w-3 h-2.5 rounded-sm inline-block bg-emerald-500"></span>% af omsætning</span>
            </div>
            <div class="overflow-y-auto" style="max-height: 520px">
              <svg :width="680" :height="60 + ressourcerData.length * 32"
                :viewBox="`0 0 680 ${60 + ressourcerData.length * 32}`" class="w-full">
                <g v-for="pct in [25, 50, 75, 100]" :key="pct">
                  <line :x1="230 + pct * 3.9" y1="10" :x2="230 + pct * 3.9" :y2="50 + ressourcerData.length * 32" stroke="#f1f5f9" stroke-width="1" />
                  <text :x="230 + pct * 3.9" y="22" font-size="8" fill="#cbd5e1" text-anchor="middle">{{ pct }}%</text>
                </g>
                <g v-for="(item, idx) in ressourcerData" :key="item.name">
                  <text x="5" :y="36 + idx * 32" font-size="10" fill="#475569" dominant-baseline="middle">
                    {{ item.name.length > 32 ? item.name.slice(0, 31) + '…' : item.name }}
                  </text>
                  <rect x="230" :y="26 + idx * 32" :width="item.bookingPct * 3.9" height="9" rx="2" fill="#3b82f6" fill-opacity="0.8" />
                  <rect x="230" :y="37 + idx * 32" :width="item.revenuePct * 3.9" height="9" rx="2" fill="#10b981" fill-opacity="0.85" />
                  <text :x="233 + Math.max(item.bookingPct, item.revenuePct) * 3.9" :y="36 + idx * 32" font-size="9" fill="#94a3b8" dominant-baseline="middle">
                    {{ item.bookingPct.toFixed(1) }}% / {{ item.revenuePct.toFixed(1) }}%
                  </text>
                </g>
              </svg>
            </div>
          </template>
        </div>

      </div>
    </div>
  </div>
</template>
