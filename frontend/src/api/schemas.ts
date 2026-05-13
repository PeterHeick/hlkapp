import { z } from 'zod'

export const CrawlPageSchema = z.object({
  url: z.string(),
  title: z.string(),
  status_code: z.number(),
  depth: z.number(),
  is_orphan: z.boolean(),
  word_count: z.number(),
})

export const CrawlLinkCountSchema = z.object({
  in: z.number(),
  out: z.number(),
})

export type LinkCount = z.infer<typeof CrawlLinkCountSchema>

export const CrawlerStatusSchema = z.object({
  running: z.boolean(),
  page_count: z.number(),
  log_tail: z.array(z.string()),
})

export const CrawlerResultsSchema = z.object({
  pages: z.array(CrawlPageSchema),
  link_counts: z.record(z.string(), CrawlLinkCountSchema),
})

export const AppSettingsSchema = z.object({
  site_url: z.string(),
  max_depth: z.number(),
  port: z.number(),
})

export type CrawlPage = z.infer<typeof CrawlPageSchema>
export type CrawlerStatus = z.infer<typeof CrawlerStatusSchema>
export type CrawlerResults = z.infer<typeof CrawlerResultsSchema>
export type AppSettings = z.infer<typeof AppSettingsSchema>
