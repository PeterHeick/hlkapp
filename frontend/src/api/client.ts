import { ofetch } from 'ofetch'

export const apiFetch = ofetch.create({
  baseURL: '/api',
  onResponseError({ response }) {
    console.error(`[api] ${response.status} ${response.url}`)
  },
})
