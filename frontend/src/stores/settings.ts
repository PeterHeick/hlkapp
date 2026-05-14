import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api/client'
import { AppSettingsSchema } from '@/api/schemas'

export const useSettingsStore = defineStore('settings', () => {
  const siteUrl = ref('')
  const maxDepth = ref(5)
  const port = ref(8765)
  const geckoToken = ref('')
  const geckoBookingUrl = ref('')
  const error = ref<string | null>(null)
  const saved = ref(false)

  async function load() {
    try {
      const data = AppSettingsSchema.parse(await apiFetch('/settings'))
      siteUrl.value = data.site_url
      maxDepth.value = data.max_depth
      port.value = data.port
      geckoToken.value = data.gecko_api_token ?? ''
      geckoBookingUrl.value = data.gecko_booking_url ?? ''
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Fejl ved indlæsning af indstillinger'
    }
  }

  async function save() {
    error.value = null
    saved.value = false
    try {
      await apiFetch('/settings', {
        method: 'PUT',
        body: { site_url: siteUrl.value, max_depth: maxDepth.value, gecko_api_token: geckoToken.value, gecko_booking_url: geckoBookingUrl.value },
      })
      saved.value = true
      setTimeout(() => { saved.value = false }, 3000)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Fejl ved gemning'
    }
  }

  return { siteUrl, maxDepth, port, geckoToken, geckoBookingUrl, error, saved, load, save }
})
