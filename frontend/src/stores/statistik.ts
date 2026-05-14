import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { apiFetch } from '@/api/client'
import {
  TreatmentResponseSchema,
  ProvidersResponseSchema,
  VolumeResponseSchema,
  RevenueResponseSchema,
  PricesSyncStatusSchema,
  ProviderBreakdownResponseSchema,
} from '@/api/schemas'
import type {
  TreatmentResponse,
  ProvidersResponse,
  VolumeResponse,
  RevenueResponse,
  ProviderBreakdownResponse,
} from '@/api/schemas'

function defaultDateFrom(): string {
  const d = new Date()
  d.setDate(d.getDate() - 90)
  return d.toISOString().slice(0, 10)
}

function defaultDateTo(): string {
  return new Date().toISOString().slice(0, 10)
}

function isoToDanish(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

function danishToIso(val: string): string | null {
  const match = val.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
  if (!match) return null
  return `${match[3]}-${match[2].padStart(2, '0')}-${match[1].padStart(2, '0')}`
}

export const useStatistikStore = defineStore('statistik', () => {
  const dateFrom = ref(defaultDateFrom())
  const dateTo   = ref(defaultDateTo())

  const displayFrom = ref(isoToDanish(dateFrom.value))
  const displayTo   = ref(isoToDanish(dateTo.value))

  watch(displayFrom, val => { const iso = danishToIso(val); if (iso) dateFrom.value = iso })
  watch(displayTo,   val => { const iso = danishToIso(val); if (iso) dateTo.value   = iso })

  const volume = ref<VolumeResponse | null>(null)
  const treatments = ref<TreatmentResponse | null>(null)
  const providers = ref<ProvidersResponse | null>(null)
  const revenue = ref<RevenueResponse | null>(null)
  const providersBreakdown = ref<ProviderBreakdownResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const priceList = ref<Record<string, number>>({})

  async function loadPrices() {
    try {
      const data = await apiFetch('/gecko/prices')
      priceList.value = (data as { prices: Record<string, number> }).prices ?? {}
    } catch {
      priceList.value = {}
    }
  }

  const syncRunning = ref(false)
  const syncCount = ref(0)
  const syncError = ref<string | null>(null)
  let syncTimer: ReturnType<typeof setInterval> | null = null

  async function loadAll() {
    loading.value = true
    error.value = null
    const params = `start=${dateFrom.value}&end=${dateTo.value}`
    try {
      const [vol, treat, prov, rev, provBreak] = await Promise.all([
        apiFetch(`/stats/bookings?${params}`),
        apiFetch(`/stats/by-treatment?${params}`),
        apiFetch(`/stats/providers?${params}`),
        apiFetch(`/stats/revenue?${params}`),
        apiFetch(`/stats/providers-by-treatment?${params}`),
      ])
      volume.value = VolumeResponseSchema.parse(vol)
      treatments.value = TreatmentResponseSchema.parse(treat)
      providers.value = ProvidersResponseSchema.parse(prov)
      revenue.value = RevenueResponseSchema.parse(rev)
      providersBreakdown.value = ProviderBreakdownResponseSchema.parse(provBreak)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Fejl ved hentning af statistik'
    } finally {
      loading.value = false
    }
  }

  async function syncPrices() {
    syncError.value = null
    try {
      await apiFetch('/gecko/sync-prices', { method: 'POST' })
      syncRunning.value = true
      syncTimer = setInterval(async () => {
        try {
          const status = PricesSyncStatusSchema.parse(await apiFetch('/gecko/prices-status'))
          syncRunning.value = status.running
          syncCount.value = status.count
          if (status.error) syncError.value = status.error
          if (!status.running && syncTimer) {
            clearInterval(syncTimer)
            syncTimer = null
          }
        } catch {
          if (syncTimer) {
            clearInterval(syncTimer)
            syncTimer = null
          }
        }
      }, 2000)
    } catch (e: unknown) {
      syncError.value = e instanceof Error ? e.message : 'Fejl ved synkronisering'
    }
  }

  return {
    dateFrom, dateTo, displayFrom, displayTo,
    volume, treatments, providers, revenue, providersBreakdown,
    priceList,
    loading, error,
    syncRunning, syncCount, syncError,
    loadAll, loadPrices, syncPrices,
  }
})
