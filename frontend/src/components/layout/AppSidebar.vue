<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { apiFetch } from '@/api/client'
import { useSyncStore } from '@/stores/sync'

function formatDanishDate(iso: string): string {
  const months = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec']
  const [y, m, d] = iso.split('-')
  return `${parseInt(d)} ${months[parseInt(m) - 1]} ${y}`
}

const appVersion = __APP_VERSION__

const route = useRoute()
const active = computed(() => route.meta.sidebarKey as string ?? '')

const connected = ref(false)
let healthTimer: ReturnType<typeof setInterval> | null = null

async function checkHealth() {
  try {
    await apiFetch('/health')
    connected.value = true
  } catch {
    connected.value = false
  }
}

const sync = useSyncStore()

onMounted(() => {
  checkHealth()
  healthTimer = setInterval(checkHealth, 10000)
  sync.start()
})
onUnmounted(() => {
  if (healthTimer) clearInterval(healthTimer)
  sync.stop()
})

const tools = [
  { key: 'seo',           path: '/#/seo',           icon: 'Globe',    label: 'SEO & Hjemmeside' },
  { key: 'indstillinger', path: '/#/indstillinger', icon: 'Settings', label: 'Indstillinger' },
]
const klinik = [
  { key: 'oversigt',     path: '/#/oversigt',     icon: 'Dashboard', label: 'Oversigt' },
  { key: 'bookinger',    path: '/#/bookinger',    icon: 'Calendar',  label: 'Bookinger' },
  { key: 'behandlinger', path: '/#/behandlinger', icon: 'Scissors',  label: 'Behandlinger' },
  { key: 'prisliste',   path: '/#/prisliste',    icon: 'List',      label: 'Prisliste' },
]
</script>

<template>
  <aside
    class="w-[220px] shrink-0 h-full bg-[#0f172a] text-slate-200 flex flex-col"
    style="font-family: Inter, system-ui, sans-serif"
  >
    <!-- Brand -->
    <div class="px-4 py-4 flex items-center gap-2.5 border-b border-slate-800/80">
      <div class="w-7 h-7 rounded-md bg-gradient-to-br from-indigo-400 to-indigo-600
                  flex items-center justify-center text-white
                  shadow-[0_1px_0_rgba(255,255,255,0.15)_inset]">
        <AppIcon name="Spark" :size="16" :stroke="2.25" />
      </div>
      <div class="leading-tight">
        <div class="text-[14px] font-semibold tracking-tight text-white">KlinikPortal</div>
        <div class="text-[10px] uppercase tracking-[0.12em] text-slate-500">Hellerup Laserklinik</div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 py-3 overflow-hidden">
      <div class="px-4 pb-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
        Værktøjer
      </div>
      <div class="flex flex-col gap-0.5">
        <a
          v-for="item in tools"
          :key="item.key"
          :href="item.path"
          class="flex items-center gap-2.5 px-3 py-2 mx-2 rounded-md text-[13px] font-medium
                 transition-colors no-underline"
          :class="active === item.key
            ? 'bg-indigo-500/15 text-white ring-1 ring-inset ring-indigo-400/25'
            : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'"
        >
          <span :class="active === item.key ? 'text-indigo-300' : 'text-slate-400'">
            <AppIcon :name="item.icon" :size="16" />
          </span>
          <span class="flex-1">{{ item.label }}</span>
        </a>
      </div>

      <div class="mt-5 px-4 pb-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
        Klinik
      </div>
      <div class="flex flex-col gap-0.5">
        <a
          v-for="item in klinik"
          :key="item.key"
          :href="item.path"
          class="flex items-center gap-2.5 px-3 py-2 mx-2 rounded-md text-[13px] font-medium
                 transition-colors no-underline"
          :class="active === item.key
            ? 'bg-indigo-500/15 text-white ring-1 ring-inset ring-indigo-400/25'
            : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'"
        >
          <span :class="active === item.key ? 'text-indigo-300' : 'text-slate-400'">
            <AppIcon :name="item.icon" :size="16" />
          </span>
          <span class="flex-1">{{ item.label }}</span>
        </a>
      </div>
    </nav>

    <!-- Sync-loading (kun synlig under aktiv hentning) -->
    <div
      v-if="sync.status && sync.status.phase !== 'idle'"
      class="mx-3 mb-2 px-3 py-2 rounded-md bg-slate-800/60 text-[11px]"
    >
      <div class="flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse shrink-0" />
        <span class="text-slate-300">
          {{ sync.status.phase === 'foreground'
            ? 'Opdaterer bookingdata...'
            : 'Henter historisk data...' }}
        </span>
      </div>
      <div v-if="sync.status.phase === 'backfill' && sync.status.pending_chunks > 0"
           class="mt-1 text-slate-500">
        {{ sync.status.pending_chunks }} perioder tilbage
      </div>
    </div>

    <!-- Footer -->
    <div class="border-t border-slate-800/80 text-[11px] text-slate-500">
      <!-- Data-rækkevidde -->
      <div class="px-4 pt-2.5 pb-1">
        <template v-if="sync.status && sync.status.oldest_booking_date">
          <span class="text-slate-400">Bookingdata: </span>
          <span class="text-slate-300">
            {{ formatDanishDate(sync.status.oldest_booking_date) }} → i dag
          </span>
        </template>
        <template v-else-if="sync.status && sync.status.booking_count === 0">
          <span class="text-slate-600 italic">Ingen bookingdata hentet endnu</span>
        </template>
      </div>
      <!-- Version og forbindelsesstatus -->
      <div class="px-4 pb-2.5 flex items-center justify-between">
        <span>v{{ appVersion }} · lokal</span>
        <span class="flex items-center gap-1.5">
          <span
            class="w-1.5 h-1.5 rounded-full transition-colors"
            :class="connected ? 'bg-emerald-400' : 'bg-slate-600'"
          />
          {{ connected ? 'Forbundet' : 'Ikke forbundet' }}
        </span>
      </div>
    </div>
  </aside>
</template>
