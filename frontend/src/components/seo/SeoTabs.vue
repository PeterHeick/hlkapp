<script setup lang="ts">
import { ref } from 'vue'
import { useCrawlerStore } from '@/stores/crawler'
import AppIcon from '@/components/layout/AppIcon.vue'
import PagesTable from './PagesTable.vue'
import StatsTable from './StatsTable.vue'
import HierarchyTable from './HierarchyTable.vue'

const crawler = useCrawlerStore()
const activeTab = ref(0)
const tabs = ['Sider & problemer', 'Sidestatistik', 'Hierarki']

function openGraph() {
  window.open('/api/crawler/graph', '_blank')
}
function openHierarchy() {
  window.open('/api/crawler/hierarchy', '_blank')
}
</script>

<template>
<div class="flex flex-col flex-1 min-h-0 overflow-hidden">
  <!-- Tab bar -->
  <div class="shrink-0 bg-white border-b border-slate-200 px-6 flex items-end gap-1">
    <button
      v-for="(tab, i) in tabs"
      :key="tab"
      @click="activeTab = i"
      class="relative px-3.5 py-2.5 text-[13px] font-medium transition-colors"
      :class="i === activeTab ? 'text-indigo-700' : 'text-slate-500 hover:text-slate-800'"
    >
      {{ tab }}
      <span v-if="i === activeTab"
        class="absolute inset-x-2 -bottom-px h-0.5 bg-indigo-600 rounded-t" />
    </button>
  </div>

  <!-- Tab content -->
  <div class="flex-1 min-h-0 overflow-auto px-6 py-4">

    <!-- Tab 0: Sider & problemer -->
    <div v-if="activeTab === 0" class="space-y-3">
      <div class="flex items-center justify-between">
        <button
          @click="openGraph"
          class="h-8 px-3 inline-flex items-center gap-1.5 rounded-md border border-slate-300
                 bg-white text-slate-700 text-[12.5px] font-medium
                 hover:border-indigo-400 hover:text-indigo-700 transition-colors"
        >
          <AppIcon name="Network" :size="13" /> Åbn interaktiv graf
        </button>
        <div class="text-[12.5px] text-slate-600">
          <span class="font-semibold text-slate-900">{{ crawler.pageCount }} sider</span>
          <span class="text-slate-400 px-1.5">·</span>
          <span class="text-amber-700 font-medium">{{ crawler.orphanCount }} forældreløse</span>
          <span class="text-slate-400 px-1.5">·</span>
          <span class="text-rose-700 font-medium">{{ crawler.errorCount }} fejl</span>
        </div>
      </div>
      <div v-if="crawler.running"
        class="rounded-md bg-indigo-50/60 border border-indigo-200/70 text-indigo-800
               text-[12px] px-3 py-2 flex items-center gap-2">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
        Crawl i gang — tabellen opdateres efter crawl er færdig.
      </div>
      <PagesTable :rows="crawler.pages" />
    </div>

    <!-- Tab 1: Sidestatistik -->
    <div v-else-if="activeTab === 1" class="space-y-3">
      <div class="text-[12.5px] text-slate-600">
        Sortérbare kolonner — klik på en kolonneoverskrift for at sortere.
      </div>
      <StatsTable :rows="crawler.pages" :link-counts="crawler.linkCounts" />
    </div>

    <!-- Tab 2: Hierarki -->
    <div v-else class="space-y-3">
      <div class="flex items-center gap-3">
        <button
          @click="openHierarchy"
          class="h-8 px-3 inline-flex items-center gap-1.5 rounded-md border border-slate-300
                 bg-white text-slate-700 text-[12.5px] font-medium
                 hover:border-indigo-400 hover:text-indigo-700 transition-colors"
        >
          <AppIcon name="Sitemap" :size="13" /> Åbn hierarki-træ
        </button>
        <span class="text-[12.5px] text-slate-500">
          Oversigt over sektioner og deres dybeste stier.
        </span>
      </div>
      <HierarchyTable :rows="crawler.hierarchySummary" />
    </div>
  </div>
</div>
</template>
