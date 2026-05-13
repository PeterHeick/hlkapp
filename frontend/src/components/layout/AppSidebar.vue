<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { apiFetch } from '@/api/client'

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

onMounted(() => {
  checkHealth()
  healthTimer = setInterval(checkHealth, 10000)
})
onUnmounted(() => { if (healthTimer) clearInterval(healthTimer) })

const tools = [
  { key: 'seo',           path: '/#/seo',           icon: 'Globe',    label: 'SEO & Hjemmeside' },
  { key: 'indstillinger', path: '/#/indstillinger',  icon: 'Settings', label: 'Indstillinger' },
]
const stubs = [
  { key: 'oversigt',     path: '/#/oversigt',     icon: 'Dashboard', label: 'Oversigt' },
  { key: 'bookinger',    path: '/#/bookinger',    icon: 'Calendar',  label: 'Bookinger' },
  { key: 'statistik',    path: '/#/statistik',    icon: 'Chart',     label: 'Statistik' },
  { key: 'behandlinger', path: '/#/behandlinger', icon: 'Scissors',  label: 'Behandlinger' },
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

      <div class="mt-5 px-4 pb-1.5 text-[10px] font-semibold uppercase tracking-[0.14em]
                  text-slate-500 flex items-center gap-1.5">
        <span>Bookinger</span>
        <span class="text-slate-600 normal-case tracking-normal font-normal">(kommer snart)</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <div
          v-for="item in stubs"
          :key="item.key"
          class="flex items-center gap-2.5 px-3 py-2 mx-2 rounded-md text-[13px]
                 font-medium text-slate-500/70 cursor-not-allowed"
        >
          <span class="text-slate-600"><AppIcon :name="item.icon" :size="16" /></span>
          <span class="flex-1">{{ item.label }}</span>
          <span class="w-1.5 h-1.5 rounded-full bg-slate-700" />
        </div>
      </div>
    </nav>

    <!-- Footer -->
    <div class="px-4 py-3 border-t border-slate-800/80 text-[11px] text-slate-500
                flex items-center justify-between">
      <span>v0.1.0 · lokal</span>
      <span class="flex items-center gap-1.5">
        <span
          class="w-1.5 h-1.5 rounded-full transition-colors"
          :class="connected ? 'bg-emerald-400' : 'bg-slate-600'"
        />
        {{ connected ? 'Forbundet' : 'Ikke forbundet' }}
      </span>
    </div>
  </aside>
</template>
