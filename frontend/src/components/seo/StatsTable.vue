<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CrawlPage } from '@/api/schemas'
import AppIcon from '@/components/layout/AppIcon.vue'
import StatusBadge from './StatusBadge.vue'

const props = defineProps<{
  rows: CrawlPage[]
  linkCounts: Record<string, { in: number; out: number }>
}>()

type SortKey = 'url' | 'status_code' | 'depth' | 'inbound' | 'outbound' | 'word_count'
const sortKey = ref<SortKey>('depth')
const sortDir = ref<'asc' | 'desc'>('asc')

function setSort(key: SortKey) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const sorted = computed(() => {
  return [...props.rows].sort((a, b) => {
    const dir = sortDir.value === 'asc' ? 1 : -1
    const aIn = props.linkCounts[a.url]?.in ?? 0
    const bIn = props.linkCounts[b.url]?.in ?? 0
    const aOut = props.linkCounts[a.url]?.out ?? 0
    const bOut = props.linkCounts[b.url]?.out ?? 0
    switch (sortKey.value) {
      case 'url':        return a.url.localeCompare(b.url) * dir
      case 'status_code': return (a.status_code - b.status_code) * dir
      case 'depth':      return (a.depth - b.depth) * dir
      case 'inbound':    return (aIn - bIn) * dir
      case 'outbound':   return (aOut - bOut) * dir
      case 'word_count': return (a.word_count - b.word_count) * dir
    }
  })
})

function rowClass(page: CrawlPage): string {
  if (page.is_orphan)          return 'bg-amber-50/40 border-l-[3px] border-l-amber-400'
  if (page.status_code >= 400) return 'bg-rose-50/40 border-l-[3px] border-l-rose-500'
  if (page.depth > 4)          return 'bg-sky-50/40 border-l-[3px] border-l-sky-400'
  return 'bg-white border-l-[3px] border-l-transparent'
}
</script>

<template>
  <div class="overflow-auto border border-slate-200 rounded-lg bg-white">
    <table class="w-full text-[12.5px]">
      <thead class="bg-slate-50 border-b border-slate-200 text-slate-600">
        <tr class="text-left">
          <th class="px-3 py-2 font-semibold">
            <button @click="setSort('url')" class="inline-flex items-center gap-1"
              :class="sortKey === 'url' ? 'text-indigo-700' : 'hover:text-slate-900'">
              URL
              <AppIcon v-if="sortKey === 'url'" :name="sortDir === 'desc' ? 'ArrowDown' : 'ArrowUp'" :size="11" :stroke="2.5"/>
            </button>
          </th>
          <th class="px-3 py-2 font-semibold">Titel</th>
          <th class="px-3 py-2 font-semibold">
            <button @click="setSort('status_code')" class="inline-flex items-center gap-1"
              :class="sortKey === 'status_code' ? 'text-indigo-700' : 'hover:text-slate-900'">
              Status
              <AppIcon v-if="sortKey === 'status_code'" :name="sortDir === 'desc' ? 'ArrowDown' : 'ArrowUp'" :size="11" :stroke="2.5"/>
            </button>
          </th>
          <th class="px-3 py-2 font-semibold text-right">
            <button @click="setSort('depth')" class="inline-flex items-center gap-1"
              :class="sortKey === 'depth' ? 'text-indigo-700' : 'hover:text-slate-900'">
              Dybde
              <AppIcon v-if="sortKey === 'depth'" :name="sortDir === 'desc' ? 'ArrowDown' : 'ArrowUp'" :size="11" :stroke="2.5"/>
            </button>
          </th>
          <th class="px-3 py-2 font-semibold text-right">
            <button @click="setSort('inbound')" class="inline-flex items-center gap-1"
              :class="sortKey === 'inbound' ? 'text-indigo-700' : 'hover:text-slate-900'">
              Indgående
              <AppIcon v-if="sortKey === 'inbound'" :name="sortDir === 'desc' ? 'ArrowDown' : 'ArrowUp'" :size="11" :stroke="2.5"/>
            </button>
          </th>
          <th class="px-3 py-2 font-semibold text-right">
            <button @click="setSort('outbound')" class="inline-flex items-center gap-1"
              :class="sortKey === 'outbound' ? 'text-indigo-700' : 'hover:text-slate-900'">
              Udgående
              <AppIcon v-if="sortKey === 'outbound'" :name="sortDir === 'desc' ? 'ArrowDown' : 'ArrowUp'" :size="11" :stroke="2.5"/>
            </button>
          </th>
          <th class="px-3 py-2 font-semibold text-right">
            <button @click="setSort('word_count')" class="inline-flex items-center gap-1"
              :class="sortKey === 'word_count' ? 'text-indigo-700' : 'hover:text-slate-900'">
              Ord
              <AppIcon v-if="sortKey === 'word_count'" :name="sortDir === 'desc' ? 'ArrowDown' : 'ArrowUp'" :size="11" :stroke="2.5"/>
            </button>
          </th>
          <th class="px-3 py-2 font-semibold">Forældrelos</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="page in sorted"
          :key="page.url"
          class="border-b border-slate-100 last:border-b-0 hover:bg-slate-50/60"
          :class="rowClass(page)"
        >
          <td class="px-3 py-1.5 max-w-[280px]">
            <div class="truncate text-[12px] text-slate-800"
              style="font-family: 'JetBrains Mono', ui-monospace, monospace">
              {{ page.url }}
            </div>
          </td>
          <td class="px-3 py-1.5 text-slate-700 max-w-[180px] truncate">{{ page.title || '—' }}</td>
          <td class="px-3 py-1.5"><StatusBadge :code="page.status_code" /></td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ page.depth }}</td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ linkCounts[page.url]?.in ?? 0 }}</td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ linkCounts[page.url]?.out ?? 0 }}</td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ page.word_count }}</td>
          <td class="px-3 py-1.5">
            <span v-if="page.is_orphan"
              class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px]
                     font-semibold ring-1 ring-inset bg-amber-50 text-amber-700 ring-amber-200">
              Ja
            </span>
            <span v-else class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px]
                     font-medium ring-1 ring-inset bg-slate-50 text-slate-500 ring-slate-200">
              Nej
            </span>
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="8" class="px-3 py-8 text-center text-[12px] text-slate-400">
            Ingen sider endnu — start en crawl
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
