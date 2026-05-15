<script setup lang="ts">
import type { CrawlPage } from '@/api/schemas'
import StatusBadge from './StatusBadge.vue'
import ProblemTag from './ProblemTag.vue'

defineProps<{ rows: CrawlPage[] }>()

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('da-DK', { day: 'numeric', month: 'short', year: 'numeric' })
}

function rowClass(page: CrawlPage): string {
  if (page.is_orphan)          return 'bg-amber-50/40 border-l-[3px] border-l-amber-400'
  if (page.status_code >= 400) return 'bg-rose-50/40 border-l-[3px] border-l-rose-500'
  if (page.depth > 4)          return 'bg-sky-50/40 border-l-[3px] border-l-sky-400'
  return 'bg-white border-l-[3px] border-l-transparent'
}

function problemKind(page: CrawlPage): string | null {
  if (page.is_orphan)          return 'orphan'
  if (page.status_code >= 400) return 'error'
  if (page.depth > 4)          return 'deep'
  return null
}
</script>

<template>
  <div class="overflow-hidden border border-slate-200 rounded-lg bg-white">
    <table class="w-full text-[12.5px]">
      <thead class="bg-slate-50 border-b border-slate-200 text-slate-600">
        <tr class="text-left">
          <th class="px-3 py-2 font-semibold w-[48%]">URL</th>
          <th class="px-3 py-2 font-semibold w-[88px]">Status</th>
          <th class="px-3 py-2 font-semibold w-[72px] text-right tabular-nums">Dybde</th>
          <th class="px-3 py-2 font-semibold w-[110px]">Sidst ændret</th>
          <th class="px-3 py-2 font-semibold">Problem</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="page in rows"
          :key="page.url"
          class="border-b border-slate-100 last:border-b-0 hover:bg-slate-50/60 transition-colors"
          :class="rowClass(page)"
        >
          <td class="px-3 py-1.5">
            <span
              class="text-[12px] text-slate-800"
              style="font-family: 'JetBrains Mono', ui-monospace, monospace"
            >{{ page.url }}</span>
          </td>
          <td class="px-3 py-1.5">
            <StatusBadge :code="page.status_code" />
          </td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ page.depth }}</td>
          <td class="px-3 py-1.5 text-slate-600 tabular-nums text-[11.5px]">{{ formatDate(page.last_modified) }}</td>
          <td class="px-3 py-1.5">
            <ProblemTag :kind="problemKind(page)" />
          </td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="5" class="px-3 py-8 text-center text-[12px] text-slate-400">
            Ingen sider endnu — start en crawl
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
