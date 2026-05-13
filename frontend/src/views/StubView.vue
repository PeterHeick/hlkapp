<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '@/components/layout/AppIcon.vue'

const route = useRoute()
const heading = computed(() => route.meta.heading as string ?? '')
const icon = computed(() => route.meta.icon as string ?? 'Dashboard')
</script>

<template>
  <div class="flex-1 flex items-center justify-center bg-slate-50 px-6">
    <div class="text-center max-w-md">
      <div class="mx-auto mb-5 w-20 h-20 rounded-2xl bg-white border border-slate-200
                  shadow-sm flex items-center justify-center text-slate-300">
        <AppIcon :name="icon" :size="40" :stroke="1.5" />
      </div>
      <h2 class="text-[20px] font-semibold text-slate-800 tracking-tight">{{ heading }}</h2>
      <p class="mt-2 text-[13.5px] text-slate-500 leading-relaxed">
        Denne funktion tilsluttes Gecko Booking API i en kommende opdatering.
      </p>
      <span class="inline-flex items-center gap-1.5 mt-5 px-2.5 py-1 rounded-full
                   bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-200
                   text-[11.5px] font-semibold uppercase tracking-wider">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500" />
        Fase 3
      </span>
    </div>
  </div>
</template>
