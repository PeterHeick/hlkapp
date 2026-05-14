import { ofetch, type FetchContext } from 'ofetch'

function onResponseError({ response }: FetchContext & { response: NonNullable<FetchContext['response']> }) {
  console.error(`[api] ${response.status} ${response.url}`)
  const detail = response._data?.detail
  if (detail) throw new Error(detail)
}

export const apiFetch = ofetch.create({
  baseURL: '/api',
  onResponseError,
})
