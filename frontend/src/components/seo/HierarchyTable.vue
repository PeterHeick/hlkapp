<script setup lang="ts">
defineProps<{
  rows: { path: string; count: number; maxDepth: number }[]
}>()
</script>

<template>
  <div class="overflow-hidden border border-slate-200 rounded-lg bg-white">
    <table class="w-full text-[12.5px]">
      <thead class="bg-slate-50 border-b border-slate-200 text-slate-600">
        <tr class="text-left">
          <th class="px-3 py-2 font-semibold">Top-sti</th>
          <th class="px-3 py-2 font-semibold text-right w-[120px] tabular-nums">Undersider</th>
          <th class="px-3 py-2 font-semibold text-right w-[120px] tabular-nums">Maks. dybde</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.path"
          class="border-b border-slate-100 last:border-b-0 hover:bg-slate-50/60"
        >
          <td class="px-3 py-1.5">
            <span class="text-[12px] text-slate-800"
              style="font-family: 'JetBrains Mono', ui-monospace, monospace">{{ row.path }}</span>
          </td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ row.count }}</td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">{{ row.maxDepth }}</td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="3" class="px-3 py-8 text-center text-[12px] text-slate-400">
            Ingen data — start en crawl
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
