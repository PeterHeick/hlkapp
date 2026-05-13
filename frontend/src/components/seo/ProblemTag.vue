<script setup lang="ts">
import AppIcon from '@/components/layout/AppIcon.vue'

const props = defineProps<{ kind: string | null }>()

const config: Record<string, { label: string; cls: string; icon: string }> = {
  orphan: { label: 'Forældreløs',  cls: 'bg-amber-100 text-amber-800',  icon: 'AlertTri' },
  error:  { label: 'Fejl',         cls: 'bg-rose-100 text-rose-800',     icon: 'XCircle' },
  deep:   { label: 'Dyb side',     cls: 'bg-sky-100 text-sky-800',       icon: 'ArrowDown' },
  redir:  { label: 'Omdirigeret',  cls: 'bg-amber-100 text-amber-800',   icon: 'ArrowUp' },
}

const entry = props.kind ? config[props.kind] ?? null : null
</script>

<template>
  <span v-if="entry"
    class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium"
    :class="entry.cls"
  >
    <AppIcon :name="entry.icon" :size="11" :stroke="2.5" />
    {{ entry.label }}
  </span>
  <span v-else class="text-slate-400 text-[12px]">—</span>
</template>
