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
  gecko_api_token: z.string(),
  gecko_booking_url: z.string(),
})

export const DiscoverResultSchema = z.object({
  site_name: z.string(),
  namespaces: z.array(z.string()),
  wp_v2_collections: z.array(z.string()),
})
export type DiscoverResult = z.infer<typeof DiscoverResultSchema>

export type CrawlPage = z.infer<typeof CrawlPageSchema>
export type CrawlerStatus = z.infer<typeof CrawlerStatusSchema>
export type CrawlerResults = z.infer<typeof CrawlerResultsSchema>
export type AppSettings = z.infer<typeof AppSettingsSchema>

export const BookingVolumeSchema = z.object({
  date: z.string(),
  count: z.number(),
  no_show_count: z.number(),
})

export const VolumeResponseSchema = z.object({
  bookings: z.array(BookingVolumeSchema),
  total: z.number(),
  no_show_total: z.number(),
})

export const TreatmentItemSchema = z.object({
  service_name: z.string(),
  booking_count: z.number(),
  no_show_count: z.number(),
  no_show_rate: z.number(),
  unit_price: z.number(),
  total_revenue: z.number(),
})

export const TreatmentResponseSchema = z.object({
  items: z.array(TreatmentItemSchema),
  total_revenue: z.number(),
})

export const ProviderStatsSchema = z.object({
  calendar_name: z.string(),
  booking_count: z.number(),
  no_show_count: z.number(),
  no_show_rate: z.number(),
  revenue: z.number(),
})

export const ProvidersResponseSchema = z.object({
  providers: z.array(ProviderStatsSchema),
})

export const RevenueResponseSchema = z.object({
  total_revenue: z.number(),
  by_service: z.record(z.string(), z.number()),
})

export const PricesSyncStatusSchema = z.object({
  running: z.boolean(),
  count: z.number(),
  error: z.string().nullable(),
})

export const ProviderTreatmentItemSchema = z.object({
  service_name: z.string(),
  count: z.number(),
  revenue: z.number(),
})

export const ProviderBreakdownSchema = z.object({
  calendar_name: z.string(),
  total_revenue: z.number(),
  total_count: z.number(),
  treatments: z.array(ProviderTreatmentItemSchema),
})

export const ProviderBreakdownResponseSchema = z.object({
  providers: z.array(ProviderBreakdownSchema),
})

export type VolumeResponse = z.infer<typeof VolumeResponseSchema>
export type TreatmentResponse = z.infer<typeof TreatmentResponseSchema>
export type ProvidersResponse = z.infer<typeof ProvidersResponseSchema>
export type RevenueResponse = z.infer<typeof RevenueResponseSchema>
export type PricesSyncStatus = z.infer<typeof PricesSyncStatusSchema>
export type ProviderBreakdownResponse = z.infer<typeof ProviderBreakdownResponseSchema>
