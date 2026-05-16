import { defineStore } from 'pinia'
import { ref, onUnmounted } from 'vue'
import { apiFetch } from '@/api/client'
import { SyncStatusSchema } from '@/api/schemas'
import type { SyncStatus } from '@/api/schemas'

export const useSyncStore = defineStore('sync', () => {
  const status = ref<SyncStatus | null>(null)
  let timer: ReturnType<typeof setInterval> | null = null

  async function poll() {
    try {
      status.value = SyncStatusSchema.parse(await apiFetch('/gecko/sync-status'))
    } catch {
      // Ignorer fejl — server er måske ikke klar endnu
    }
  }

  function start() {
    if (timer) return
    poll()
    timer = setInterval(poll, 5000)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  const isActive = () => !!timer

  return { status, start, stop, isActive, poll }
})
