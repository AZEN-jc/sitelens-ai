import type { Scan } from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || data.error || `Request failed (${response.status})`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  scans: (limit = 30, offset = 0) => request<Scan[]>(`/scans?limit=${limit}&offset=${offset}`),
  scanCount: () => request<{ count: number }>('/scans/count'),
  scan: (id: string | number) => request<Scan>(`/scans/${id}`),
  createScan: (url: string) => request<Scan>('/scans', { method: 'POST', body: JSON.stringify({ url, authorized: true }) }),
  compare: (first_scan_id: number, second_scan_id: number) => request<Record<string, unknown>>('/scans/compare', {
    method: 'POST', body: JSON.stringify({ first_scan_id, second_scan_id }),
  }),
  aiStatus: () => request<{ configured: boolean; base_url?: string; model?: string }>('/ai/config'),
  configureAI: (base_url: string, api_key: string, model: string) => request('/ai/config', {
    method: 'POST', body: JSON.stringify({ base_url, api_key, model }),
  }),
  clearAI: () => request<void>('/ai/config', { method: 'DELETE' }),
  testAI: () => request<{ ok: boolean; error?: string }>('/ai/test', { method: 'POST' }),
  analyze: (scan_id: number) => request('/ai/analyze', {
    method: 'POST', body: JSON.stringify({ scan_id, confirm_data_sent: true }),
  }),
  reports: () => request<{ id: number; scan_id: number; model: string; content: string; created_at: string }[]>('/reports'),
}

export function reportUrl(scanId: number, format: 'html' | 'json') {
  return `/api/reports/${scanId}/export?format=${format}`
}
