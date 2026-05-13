<script setup lang="ts">
import AppIcon from '@/components/layout/AppIcon.vue'
defineProps<{ code: number }>()
</script>

<template>
  <span
    class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-semibold ring-1 ring-inset"
    :class="{
      'bg-emerald-50 text-emerald-700 ring-emerald-200': code >= 200 && code < 300,
      'bg-amber-50 text-amber-700 ring-amber-200':       code >= 300 && code < 400,
      'bg-rose-50 text-rose-700 ring-rose-200':          code >= 400 || code === 0,
    }"
  >
    <AppIcon
      :name="code >= 200 && code < 300 ? 'Check' : code >= 300 && code < 400 ? 'ArrowUp' : 'XCircle'"
      :size="11"
      :stroke="2.5"
    />
    {{ code === 0 ? '???' : code }}
  </span>
</template>
