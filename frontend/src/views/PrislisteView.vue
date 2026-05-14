<script setup lang="ts">
import { onMounted } from 'vue'
import { useStatistikStore } from '@/stores/statistik'
import AppIcon from '@/components/layout/AppIcon.vue'

const stat = useStatistikStore()
onMounted(() => stat.loadPrices())
</script>

<template>
  <div class="flex-1 overflow-auto px-6 py-6 bg-slate-50">
    <div class="max-w-[600px] mx-auto space-y-4">

      <!-- Header + opdater-knap -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-[15px] font-semibold text-slate-900">Prisliste</h1>
          <p class="text-[12px] text-slate-500 mt-0.5">Behandlingspriser hentet fra Gecko booking-siden.</p>
        </div>
        <button
          @click="stat.syncPrices()"
          :disabled="stat.syncRunning"
          class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md border border-slate-300
                 bg-white text-slate-700 text-[12.5px] font-medium
                 hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <AppIcon name="Search" :size="13" />
          {{ stat.syncRunning ? `Henter... (${stat.syncCount})` : 'Opdater priser' }}
        </button>
      </div>

      <!-- Fejl / success -->
      <div v-if="stat.syncError" class="rounded-md bg-rose-50 border border-rose-200 px-4 py-3 text-[12.5px] text-rose-700">
        {{ stat.syncError }}
      </div>
      <div v-if="!stat.syncRunning && stat.syncCount > 0" class="rounded-md bg-emerald-50 border border-emerald-200 px-4 py-3 text-[12.5px] text-emerald-700">
        {{ stat.syncCount }} behandlinger hentet.
      </div>

      <!-- Prisliste -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <p v-if="Object.keys(stat.priceList).length === 0"
          class="text-[12.5px] text-slate-400 text-center py-10">
          Ingen priser — klik "Opdater priser" eller sæt booking-URL under Indstillinger
        </p>
        <table v-else class="w-full text-[12.5px]">
          <thead>
            <tr class="border-b border-slate-200">
              <th class="text-left font-semibold text-slate-700 px-5 py-3">Behandling</th>
              <th class="text-right font-semibold text-slate-700 px-5 py-3">Pris</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(price, name) in stat.priceList" :key="name"
              class="border-b border-slate-50 hover:bg-slate-50">
              <td class="py-2 px-5 text-slate-800">{{ name }}</td>
              <td class="py-2 px-5 text-right tabular-nums text-slate-700">
                {{ price > 0 ? price.toLocaleString('da-DK', { maximumFractionDigits: 0 }) + ' kr' : '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>
