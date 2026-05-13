<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const route = useRoute()
const title = computed(() => route.meta.title as string ?? '')
const breadcrumb = computed(() => route.meta.breadcrumb as string | undefined)
</script>

<template>
  <div class="flex h-screen bg-slate-50" style="font-family: Inter, system-ui, sans-serif">
    <AppSidebar />
    <main class="flex-1 min-w-0 flex flex-col overflow-hidden">
      <header class="h-[56px] shrink-0 bg-white border-b border-slate-200 px-6 flex items-center">
        <div class="flex items-baseline gap-2">
          <h1 class="text-[15px] font-semibold text-slate-900 tracking-tight m-0">{{ title }}</h1>
          <span v-if="breadcrumb" class="text-[12px] text-slate-500">/ {{ breadcrumb }}</span>
        </div>
      </header>
      <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
        <RouterView />
      </div>
    </main>
  </div>
</template>
