<script setup lang="ts">
defineProps<{ status: string; count: number; crawling: boolean }>()
</script>

<template>
  <div class="h-[40px] shrink-0 bg-slate-50 border-b border-slate-200 px-6 flex items-center gap-4">
    <div class="flex items-center gap-2 min-w-[260px]">
      <span
        class="w-2 h-2 rounded-full"
        :class="crawling ? 'bg-indigo-500 animate-pulse' : 'bg-emerald-500'"
      />
      <span class="text-[12.5px] text-slate-700">{{ status }}</span>
    </div>

    <div class="flex-1 h-1.5 rounded-full bg-slate-200 overflow-hidden relative">
      <div v-if="crawling" class="kp-indeterminate h-full" />
      <div v-else class="h-full bg-emerald-500 rounded-full w-full" />
    </div>

    <div class="text-[12.5px] text-slate-600 tabular-nums min-w-[80px] text-right">
      Sider: <span class="font-semibold text-slate-900">{{ count }}</span>
    </div>
  </div>
</template>
