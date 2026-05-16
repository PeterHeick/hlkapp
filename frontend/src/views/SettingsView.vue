<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useStatistikStore } from '@/stores/statistik'
import { useSyncStore } from '@/stores/sync'
import AppIcon from '@/components/layout/AppIcon.vue'
import { apiFetch } from '@/api/client'
import { DiscoverResultSchema, PriceLogSchema } from '@/api/schemas'
import type { DiscoverResult, PriceLogEntry } from '@/api/schemas'

const settings = useSettingsStore()
const statistik = useStatistikStore()
const sync = useSyncStore()
onMounted(() => {
  settings.load()
  sync.poll()
  loadPriceLog()
})

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

const shuttingDown = ref(false)

async function shutdown() {
  if (!confirm('Luk serveren ned?')) return
  shuttingDown.value = true
  try {
    await apiFetch('/shutdown', { method: 'POST' })
  } catch {
    // Server lukker forbindelsen — forventet
  }
}

// Nulstil booking-cache
const resetting = ref(false)
const resetError = ref<string | null>(null)
const resetOk = ref(false)

async function resetCache() {
  if (!confirm('Nulstil booking-cache? Alle cachede bookinger slettes og hentes igen. Crawl-data bevares.')) return
  resetting.value = true
  resetError.value = null
  resetOk.value = false
  try {
    await apiFetch('/gecko/reset', { method: 'POST' })
    resetOk.value = true
    setTimeout(() => { resetOk.value = false }, 4000)
    await sync.poll()
  } catch (e: unknown) {
    resetError.value = e instanceof Error ? e.message : 'Fejl ved nulstilling'
  } finally {
    resetting.value = false
  }
}

// Anvend priser manuelt
const applyingPrices = ref(false)
const applyPricesError = ref<string | null>(null)
const applyPricesOk = ref(false)

async function applyPrices() {
  applyingPrices.value = true
  applyPricesError.value = null
  applyPricesOk.value = false
  try {
    await apiFetch('/gecko/apply-prices', { method: 'POST' })
    applyPricesOk.value = true
    setTimeout(() => { applyPricesOk.value = false }, 4000)
    await sync.poll()
    await loadPriceLog()
  } catch (e: unknown) {
    applyPricesError.value = e instanceof Error ? e.message : 'Fejl ved prisberegning'
  } finally {
    applyingPrices.value = false
  }
}

// Price-log
const priceLogEntries = ref<PriceLogEntry[]>([])

async function loadPriceLog() {
  try {
    const data = PriceLogSchema.parse(await apiFetch('/gecko/price-log'))
    priceLogEntries.value = data.entries
  } catch {
    priceLogEntries.value = []
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
        <div class="px-5 pt-4 pb-3 border-b border-slate-100">
          <h2 class="text-[14px] font-semibold text-slate-900 m-0">Gecko Booking API</h2>
          <p class="text-[12px] text-slate-500 mt-0.5">Forbindelse til booking-systemet.</p>
        </div>
        <div class="px-5 py-5 space-y-4">
          <div class="space-y-1.5">
            <label class="text-[12.5px] font-medium text-slate-800 block">API Token</label>
            <input
              v-model="settings.geckoToken"
              type="password"
              placeholder="Indsæt token fra Gecko Booking"
              class="w-full h-9 px-3 rounded-md bg-white border border-slate-300 text-[13px]
                     text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-200
                     focus:border-indigo-400"
              style="font-family: 'JetBrains Mono', ui-monospace, monospace"
            />
          </div>
          <button
            @click="settings.save()"
            class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md bg-indigo-600
                   hover:bg-indigo-700 text-white text-[12.5px] font-semibold shadow-sm
                   transition-colors"
          >
            <AppIcon name="Save" :size="13" /> Gem token
          </button>

          <hr class="border-slate-100" />

          <div class="space-y-2">
            <div>
              <p class="text-[12.5px] font-medium text-slate-800">Behandlingspriser</p>
              <p class="text-[11.5px] text-slate-500 mt-0.5">
                Henter priser fra Gecko bookingsiden og gemmer dem lokalt til omsætningsberegning.
              </p>
            </div>
            <div class="space-y-1.5">
              <label class="text-[12.5px] font-medium text-slate-800 block">Booking-side URL</label>
              <input
                v-model="settings.geckoBookingUrl"
                type="url"
                placeholder="https://klinik.app.geckobooking.dk/site/booking.php?..."
                class="w-full h-9 px-3 rounded-md bg-white border border-slate-300 text-[12px]
                       text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-200
                       focus:border-indigo-400"
                style="font-family: 'JetBrains Mono', ui-monospace, monospace"
              />
              <p class="text-[11px] text-slate-400">Den offentlige booking-URL med icCode og bId parametre.</p>
            </div>
            <button
              @click="statistik.syncPrices()"
              :disabled="statistik.syncRunning"
              class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md border border-slate-300
                     bg-white text-slate-700 text-[12.5px] font-medium
                     hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <AppIcon name="Search" :size="13" />
              {{ statistik.syncRunning ? `Henter... (${statistik.syncCount})` : 'Opdater priser' }}
            </button>
            <div v-if="statistik.syncError" class="text-[12px] text-rose-700">
              {{ statistik.syncError }}
            </div>
            <div v-if="!statistik.syncRunning && statistik.syncCount > 0" class="text-[12px] text-emerald-700">
              {{ statistik.syncCount }} behandlinger hentet.
            </div>
          </div>
        </div>
      </div>

      <!-- Migrationsadvarsel -->
      <div
        v-if="sync.status?.migration_warning"
        class="rounded-md bg-amber-50 border border-amber-300 px-4 py-3 text-[12.5px] text-amber-800"
      >
        <div class="flex items-start gap-2">
          <AppIcon name="AlertTri" :size="14" class="shrink-0 mt-0.5" />
          <span>{{ sync.status.migration_warning }}</span>
        </div>
      </div>

      <!-- Booking-cache sektion -->
      <div class="bg-white border border-slate-200 rounded-lg shadow-sm">
        <div class="px-5 pt-4 pb-3 border-b border-slate-100">
          <h2 class="text-[14px] font-semibold text-slate-900 m-0">Booking-cache</h2>
          <p class="text-[12px] text-slate-500 mt-0.5">
            Bookinger fra Gecko gemmes lokalt og prissættes med daterede prislister.
          </p>
        </div>
        <div class="px-5 py-5 space-y-4">

          <!-- Sync-status -->
          <div v-if="sync.status" class="space-y-1.5">
            <div class="text-[12.5px] font-medium text-slate-800">Status</div>
            <div class="flex items-center gap-2 text-[12px]">
              <span
                class="w-2 h-2 rounded-full shrink-0"
                :class="{
                  'bg-indigo-400 animate-pulse': sync.status.phase !== 'idle',
                  'bg-slate-300': sync.status.phase === 'idle',
                }"
              />
              <span class="text-slate-600">
                <template v-if="sync.status.phase === 'backfill'">
                  Baggrundshentning: {{ sync.status.chunks_done }} / {{ sync.status.chunks_total }} perioder hentet
                </template>
                <template v-else-if="sync.status.phase === 'foreground'">
                  Henter data til valgt periode...
                </template>
                <template v-else>
                  {{ sync.status.chunks_done }} / {{ sync.status.chunks_total }} perioder hentet
                </template>
              </span>
            </div>
            <div v-if="sync.status.last_priced_at" class="text-[11.5px] text-slate-400">
              Sidst prissatte: {{ sync.status.last_priced_at.replace('T', ' ').slice(0, 16) }}
            </div>
            <div v-if="sync.status.error" class="text-[12px] text-rose-700">
              Fejl: {{ sync.status.error }}
            </div>
          </div>

          <hr class="border-slate-100" />

          <!-- Anvend priser -->
          <div class="space-y-2">
            <div>
              <p class="text-[12.5px] font-medium text-slate-800">Anvend priser</p>
              <p class="text-[11.5px] text-slate-500 mt-0.5">
                Prissæt bookinger der mangler pris ud fra filer i <code class="font-mono">data/prislister/</code>.
                Kører automatisk efter sync, men kan startes manuelt her.
              </p>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button
                @click="applyPrices()"
                :disabled="applyingPrices"
                class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md border border-slate-300
                       bg-white text-slate-700 text-[12.5px] font-medium
                       hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <AppIcon :name="applyingPrices ? 'RefreshCw' : 'Tag'" :size="13" />
                {{ applyingPrices ? 'Beregner...' : 'Anvend priser' }}
              </button>
            </div>
            <div v-if="applyPricesError" class="text-[12px] text-rose-700">{{ applyPricesError }}</div>
            <div v-if="applyPricesOk" class="text-[12px] text-emerald-700">Priser anvendt.</div>
          </div>

          <hr class="border-slate-100" />

          <!-- Nulstil cache -->
          <div class="space-y-2">
            <div>
              <p class="text-[12.5px] font-medium text-slate-800">Nulstil booking-cache</p>
              <p class="text-[11.5px] text-slate-500 mt-0.5">
                Sletter alle cachede bookinger og starter hentning forfra. SEO-crawl-data bevares.
              </p>
            </div>
            <button
              @click="resetCache()"
              :disabled="resetting"
              class="h-8 px-4 inline-flex items-center gap-1.5 rounded-md border border-rose-300
                     bg-white text-rose-700 text-[12.5px] font-medium
                     hover:bg-rose-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <AppIcon name="Trash" :size="13" />
              {{ resetting ? 'Nulstiller...' : 'Nulstil cache' }}
            </button>
            <div v-if="resetError" class="text-[12px] text-rose-700">{{ resetError }}</div>
            <div v-if="resetOk" class="text-[12px] text-emerald-700">Cache nulstillet — baggrundshentning startet.</div>
          </div>
        </div>
      </div>

      <!-- Price-log (uprissatte services) -->
      <div v-if="priceLogEntries.length > 0" class="bg-white border border-amber-200 rounded-lg shadow-sm">
        <div class="px-5 pt-4 pb-3 border-b border-amber-100">
          <h2 class="text-[14px] font-semibold text-amber-800 m-0">Uprissatte behandlinger</h2>
          <p class="text-[12px] text-slate-500 mt-0.5">
            Disse behandlinger findes ikke i nogen prisliste og har fået pris = 0 kr.
          </p>
        </div>
        <div class="px-5 py-4 space-y-3">
          <div v-for="entry in priceLogEntries.slice(0, 5)" :key="entry.logged_at" class="space-y-1">
            <div class="text-[11px] text-slate-400">{{ entry.logged_at.replace('T', ' ').slice(0, 16) }}</div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="svc in entry.unknown_services"
                :key="svc"
                class="px-1.5 py-0.5 rounded bg-amber-50 border border-amber-200 text-amber-800 text-[11px]"
              >{{ svc }}</span>
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

      <!-- Luk server -->
      <div class="bg-white border border-rose-200 rounded-lg shadow-sm">
        <div class="px-5 pt-4 pb-3 border-b border-rose-100">
          <h2 class="text-[14px] font-semibold text-rose-700 m-0">Luk server</h2>
          <p class="text-[12px] text-slate-500 mt-0.5">Lukker KlinikPortal-serveren helt ned.</p>
        </div>
        <div class="px-5 py-4">
          <button
            @click="shutdown"
            :disabled="shuttingDown"
            class="h-9 px-4 inline-flex items-center gap-1.5 rounded-md bg-rose-600
                   hover:bg-rose-700 text-white text-[13px] font-semibold shadow-sm
                   transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <AppIcon name="Power" :size="13" />
            {{ shuttingDown ? 'Lukker ned...' : 'Luk server' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
