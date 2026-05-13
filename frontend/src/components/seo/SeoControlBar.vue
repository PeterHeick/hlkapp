<script setup lang="ts">
import AppIcon from '@/components/layout/AppIcon.vue'

defineProps<{ url: string; depth: number; crawling: boolean }>()
const emit = defineEmits<{
  'update:url': [value: string]
  'update:depth': [value: number]
  start: []
  stop: []
}>()
</script>

<template>
  <div class="h-[56px] shrink-0 bg-white border-b border-slate-200 px-6 flex items-center gap-3">
    <label class="text-[12.5px] font-medium text-slate-700 shrink-0">Hjemmeside URL:</label>

    <div class="flex-1 relative">
      <input
        :value="url"
        @input="emit('update:url', ($event.target as HTMLInputElement).value)"
        placeholder="https://www.example.com"
        class="w-full h-9 px-3 pr-9 rounded-md bg-slate-50 border border-slate-300
               text-[13px] text-slate-800 font-mono placeholder-slate-400
               focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400"
        style="font-family: 'JetBrains Mono', ui-monospace, monospace"
      />
      <span class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400">
        <AppIcon name="Search" :size="14" />
      </span>
    </div>

    <label class="text-[12.5px] font-medium text-slate-700 shrink-0 pl-1">Maks. dybde:</label>
    <div class="relative">
      <select
        :value="depth"
        @change="emit('update:depth', Number(($event.target as HTMLSelectElement).value))"
        class="appearance-none h-9 pl-3 pr-8 rounded-md bg-white border border-slate-300
               text-[13px] text-slate-800 font-medium
               focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400"
      >
        <option v-for="n in [2,3,4,5,6,7,8]" :key="n" :value="n">{{ n }}</option>
      </select>
      <span class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
        <AppIcon name="ChevronDown" :size="14" />
      </span>
    </div>

    <button
      :disabled="crawling"
      @click="emit('start')"
      class="h-9 px-3.5 inline-flex items-center gap-1.5 rounded-md text-[13px]
             font-semibold transition-colors shadow-sm"
      :class="crawling
        ? 'bg-emerald-600/40 text-white/70 cursor-not-allowed'
        : 'bg-emerald-600 hover:bg-emerald-700 text-white'"
    >
      <AppIcon name="Play" :size="13" :stroke="2.5" /> Start crawl
    </button>

    <button
      :disabled="!crawling"
      @click="emit('stop')"
      class="h-9 px-3.5 inline-flex items-center gap-1.5 rounded-md text-[13px]
             font-semibold transition-colors shadow-sm"
      :class="crawling
        ? 'bg-rose-600 hover:bg-rose-700 text-white'
        : 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200'"
    >
      <AppIcon name="StopSquare" :size="12" :stroke="2.5" /> Stop
    </button>
  </div>
</template>
