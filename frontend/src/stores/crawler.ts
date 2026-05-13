import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api/client'
import type { CrawlPage, CrawlerResults } from '@/api/schemas'

export const useCrawlerStore = defineStore('crawler', () => {
  const url = ref('')
  const depth = ref(5)
  const running = ref(false)
  const pageCount = ref(0)
  const statusText = ref('Klar')
  const error = ref<string | null>(null)
  const pages = ref<CrawlPage[]>([])
  const linkCounts = ref<Record<string, { in: number; out: number }>>({} as Record<string, { in: number; out: number }>)

  let pollTimer: ReturnType<typeof setInterval> | null = null
  let finishing = false

  const orphanCount = computed(() => pages.value.filter((p: CrawlPage) => p.is_orphan).length)
  const errorCount = computed(() => pages.value.filter((p: CrawlPage) => p.status_code >= 400).length)

  const hierarchySummary = computed(() => {
    const map = new Map<string, { count: number; maxDepth: number }>()
    for (const page of pages.value) {
      try {
        const parts = new URL(page.url).pathname.split('/').filter(Boolean)
        const top = parts.length ? '/' + parts[0] : '/'
        const entry = map.get(top) ?? { count: 0, maxDepth: 0 }
        entry.count++
        entry.maxDepth = Math.max(entry.maxDepth, page.depth)
        map.set(top, entry)
      } catch { /* ugyldig URL */ }
    }
    return [...map.entries()]
      .map(([path, v]) => ({ path, ...v }))
      .sort((a, b) => a.path.localeCompare(b.path))
  })

  async function start() {
    error.value = null
    try {
      running.value = true
      pageCount.value = 0
      pages.value = []
      linkCounts.value = {}
      statusText.value = `Crawling: ${url.value}`
      await apiFetch('/crawler/start', {
        method: 'POST',
        body: { url: url.value, depth: depth.value },
      })
      pollTimer = setInterval(poll, 2000)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Ukendt fejl ved start'
      running.value = false
      statusText.value = 'Fejl ved start — se fejlbesked'
    }
  }

  async function stop() {
    try {
      await apiFetch('/crawler/stop', { method: 'POST' })
    } catch { /* ignorér — kan allerede være stoppet */ }
    await finish()
  }

  async function poll() {
    try {
      const status = await apiFetch<{ running: boolean; page_count: number; log_tail: string[] }>(
        '/crawler/status',
      )
      pageCount.value = status.page_count
      if (status.log_tail?.length) {
        const last = status.log_tail[status.log_tail.length - 1]
        statusText.value = last.length > 120 ? last.slice(-120) : last
      }
      if (!status.running) {
        await finish()
      }
    } catch { /* netværksfejl under crawl — ignorer og prøv igen */ }
  }

  async function finish() {
    if (finishing) return
    finishing = true
    try {
      if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
      running.value = false
      statusText.value = 'Kører analyse...'
      await apiFetch('/crawler/finish', { method: 'POST' })
      await loadResults()
      statusText.value =
        `Analyse færdig — ${orphanCount.value} forældreløse · ${errorCount.value} fejl`
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Fejl ved indlæsning af resultater'
      statusText.value = 'Fejl ved analyse — se fejlbesked'
    } finally {
      finishing = false
    }
  }

  async function loadResults() {
    const data = await apiFetch<CrawlerResults>('/crawler/results')
    pages.value = data.pages
    linkCounts.value = data.link_counts as Record<string, { in: number; out: number }>
    pageCount.value = data.pages.length
  }

  async function restoreSession() {
    try {
      const status = await apiFetch<{ running: boolean; page_count: number }>(
        '/crawler/status',
      )
      if (status.page_count > 0 && !status.running) {
        await loadResults()
        statusText.value = `Tidligere session — ${pages.value.length} sider`
      } else if (status.running) {
        running.value = true
        pageCount.value = status.page_count
        statusText.value = `Crawl kører (${status.page_count} sider)...`
        pollTimer = setInterval(poll, 2000)
      }
    } catch { /* backend ikke klar endnu */ }
  }

  return {
    url, depth, running, pageCount, statusText, error,
    pages, linkCounts, orphanCount, errorCount, hierarchySummary,
    start, stop, restoreSession,
  }
})
