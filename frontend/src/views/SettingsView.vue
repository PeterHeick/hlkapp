<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import AppIcon from '@/components/layout/AppIcon.vue'
import { apiFetch } from '@/api/client'
import { DiscoverResultSchema } from '@/api/schemas'
import type { DiscoverResult } from '@/api/schemas'

const settings = useSettingsStore()
onMounted(() => settings.load())

const discovering = ref(false)
const discoverResult = ref<DiscoverResult | null>(null)
const discoverError = ref<string | null>(null)

async function discoverApi() {
  discovering.value = true
  discoverError.value = null
  discoverResult.value = null
  try {
    discoverResult.value = DiscoverResultSchema.parse(await apiFetch('/crawler/discover'))
  } catch (e: unknown) {
    discoverError.value = e instanceof Error ? e.message : 'Ukendt fejl'
  } finally {
    discovering.value = false
  }
}
</script>

<template>
  <div class="flex-1 overflow-auto px-6 py-8 bg-slate-50">
    <div class="max-w-[600px] mx-auto space-y-5">

      <!-- Hjemmeside-sektion -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm">
        <div class="px-5 pt-4 pb-3 border-b border-slate-100">
          <h2 class="text-[14px] font-semibold text-slate-900 m-0">Hjemmeside</h2>
          <p class="text-[12px] text-slate-500 mt-0.5">URL og indstillinger der bruges når du starter et crawl.</p>
        </div>
        <div class="px-5 py-5 space-y-4">
          <div class="space-y-1.5">
            <label class="text-[12.5px] font-medium text-slate-800 block">Hjemmeside URL</label>
            <input
              v-model="settings.siteUrl"
              class="w-full h-9 px-3 rounded-md bg-white border border-slate-300 text-[13px]
                     text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-200
                     focus:border-indigo-400"
              style="font-family: 'JetBrains Mono', ui-monospace, monospace"
            />
          </div>
          <div class="space-y-1.5">
            <label class="text-[12.5px] font-medium text-slate-800 block">Maks. crawl-dybde</label>
            <p class="text-[11.5px] text-slate-500">Mellem 2 og 8. Dybere crawls tager længere tid.</p>
            <input
              v-model.number="settings.maxDepth"
              type="number" min="2" max="8"
              class="w-32 h-9 px-3 rounded-md bg-white border border-slate-300 text-[13px]
                     text-slate-800 tabular-nums focus:outline-none focus:ring-2
                     focus:ring-indigo-200 focus:border-indigo-400"
            />
          </div>
        </div>
      </div>

      <!-- Gecko API sektion -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm">
        <div class="px-5 pt-4 pb-3 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 class="text-[14px] font-semibold text-slate-900 m-0">Gecko Booking API</h2>
            <p class="text-[12px] text-slate-500 mt-0.5">Forbindelse til booking-systemet.</p>
          </div>
          <span class="text-[10.5px] uppercase tracking-wider px-2 py-0.5 rounded
                       bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200">
            Fase 3
          </span>
        </div>
        <div class="px-5 py-5">
          <div class="space-y-1.5">
            <label class="text-[12.5px] font-medium text-slate-800 block">API Token</label>
            <p class="text-[11.5px] text-slate-500">Tilsluttes i en kommende opdatering.</p>
            <div class="relative">
              <input
                type="password"
                disabled
                placeholder="Ikke aktiv endnu"
                class="w-full h-9 px-3 pr-9 rounded-md bg-slate-50 border border-slate-200
                       text-[13px] text-slate-400 cursor-not-allowed"
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                <AppIcon name="Lock" :size="14" />
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Diagnostik -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm">
        <div class="px-5 pt-4 pb-3 border-b border-slate-100">
          <h2 class="text-[14px] font-semibold text-slate-900 m-0">Diagnostik</h2>
          <p class="text-[12px] text-slate-500 mt-0.5">Tjek hvilke WordPress REST API endpoints sitet eksponerer.</p>
        </div>
        <div class="px-5 py-4 space-y-3">
          <button
            @click="discoverApi"
            :disabled="discovering"
            class="h-9 px-4 inline-flex items-center gap-1.5 rounded-md border border-slate-300
                   bg-white text-slate-700 text-[13px] font-medium
                   hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <AppIcon name="Search" :size="13" />
            {{ discovering ? 'Henter...' : 'Tjek WP API' }}
          </button>
          <div v-if="discoverError" class="text-[12px] text-rose-700">{{ discoverError }}</div>
          <template v-if="discoverResult">
            <div class="text-[12px] text-slate-600">
              <span class="font-medium">Site:</span> {{ discoverResult.site_name }}
            </div>
            <div class="text-[12px] text-slate-600">
              <span class="font-medium">Namespaces:</span> {{ discoverResult.namespaces.join(', ') }}
            </div>
            <div class="text-[12px] text-slate-600 font-medium">
              wp/v2 collections ({{ discoverResult.wp_v2_collections.length }}):
            </div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="col in discoverResult.wp_v2_collections"
                :key="col"
                class="px-1.5 py-0.5 rounded bg-slate-50 border border-slate-200 text-slate-700"
                style="font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 11px"
              >{{ col }}</span>
            </div>
          </template>
        </div>
      </div>

      <!-- Fejl / success -->
      <div v-if="settings.error" class="rounded-md bg-rose-50 border border-rose-200
           px-4 py-3 text-[12.5px] text-rose-700">
        {{ settings.error }}
      </div>
      <div v-if="settings.saved" class="rounded-md bg-emerald-50 border border-emerald-200
           px-4 py-3 text-[12.5px] text-emerald-700">
        Indstillinger gemt.
      </div>

      <!-- Gem-knapper -->
      <div class="flex justify-end gap-2 pt-1">
        <button
          @click="settings.load()"
          class="h-9 px-4 rounded-md border border-slate-300 bg-white text-slate-700
                 text-[13px] font-medium hover:bg-slate-50 transition-colors"
        >
          Annullér
        </button>
        <button
          @click="settings.save()"
          class="h-9 px-4 inline-flex items-center gap-1.5 rounded-md bg-indigo-600
                 hover:bg-indigo-700 text-white text-[13px] font-semibold shadow-sm
                 transition-colors"
        >
          <AppIcon name="Save" :size="13" /> Gem indstillinger
        </button>
      </div>
    </div>
  </div>
</template>
