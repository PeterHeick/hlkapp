<script setup lang="ts">
import AppIcon from '@/components/layout/AppIcon.vue'

function download(type: 'inventory' | 'matrix' | 'todo') {
  const names: Record<string, string> = {
    inventory: 'inventory_full.csv',
    matrix:    'link_matrix.csv',
    todo:      'todo_reparations.csv',
  }
  const a = document.createElement('a')
  a.href = `/api/crawler/export/${type}`
  a.download = names[type]
  a.click()
}
</script>

<template>
  <div class="h-[52px] shrink-0 bg-white border-t border-slate-200 px-6 flex items-center gap-2">
    <span class="text-[12.5px] font-medium text-slate-700 mr-1">Eksporter:</span>
    <button
      v-for="[type, label] in [['inventory', 'Inventory (CSV)'], ['matrix', 'Link Matrix (CSV)'], ['todo', 'To-Do reparationer (CSV)']]"
      :key="type"
      @click="download(type as 'inventory' | 'matrix' | 'todo')"
      class="h-8 px-3 inline-flex items-center gap-1.5 rounded-md border border-slate-300
             bg-white text-slate-700 text-[12.5px] font-medium
             hover:border-slate-400 hover:bg-slate-50 transition-colors"
    >
      <AppIcon name="Save" :size="12" />
      {{ label }}
    </button>
  </div>
</template>
