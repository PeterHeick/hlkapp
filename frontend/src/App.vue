<script setup lang="ts">
import { onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useCrawlerStore } from '@/stores/crawler'
import { useSettingsStore } from '@/stores/settings'

const crawler = useCrawlerStore()
const settings = useSettingsStore()

onMounted(async () => {
  await settings.load()
  await crawler.restoreSession()
})
</script>

<template>
  <AppLayout />
</template>
