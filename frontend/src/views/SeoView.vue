<script setup lang="ts">
import { useCrawlerStore } from '@/stores/crawler'
import SeoControlBar from '@/components/seo/SeoControlBar.vue'
import StatusStrip from '@/components/seo/StatusStrip.vue'
import SeoTabs from '@/components/seo/SeoTabs.vue'
import ExportFooter from '@/components/seo/ExportFooter.vue'

const crawler = useCrawlerStore()
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Fejlbesked -->
    <div v-if="crawler.error"
      class="shrink-0 bg-rose-50 border-b border-rose-200 px-6 py-2 text-[12.5px]
             text-rose-700 flex items-center gap-2">
      <span class="font-medium">Fejl:</span> {{ crawler.error }}
      <button @click="crawler.error = null" class="ml-auto text-rose-400 hover:text-rose-600">×</button>
    </div>

    <SeoControlBar
      :depth="crawler.depth"
      :crawling="crawler.running"
      @update:depth="crawler.depth = $event"
      @start="crawler.start()"
      @stop="crawler.stop()"
    />
    <StatusStrip
      :status="crawler.statusText"
      :count="crawler.pageCount"
      :crawling="crawler.running"
    />
    <SeoTabs />
    <ExportFooter />
  </div>
</template>
