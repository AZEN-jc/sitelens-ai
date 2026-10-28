import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import ReportsView from '../src/views/ReportsView.vue'
import { api } from '../src/api'
import type { Scan } from '../src/types'

vi.mock('../src/api', () => ({
  api: { scans: vi.fn(), scanCount: vi.fn() },
  reportUrl: (id: number, format: string) => `/api/reports/${id}/export?format=${format}`,
}))

function scan(id: number): Scan {
  return {
    id, url: `https://example.test/${id}`, final_url: `https://example.test/${id}`,
    status_code: 200, content_type: 'text/html', title: `记录 ${id}`, headers: {}, meta: [],
    scripts: [], styles: [], created_at: '2026-10-01T00:00:00Z', technologies: [],
    ai_report_count: 0, ai_reports: [],
  }
}

describe('ReportsView history paging', () => {
  it('loads older reports on demand and stops at the total count', async () => {
    vi.mocked(api.scans)
      .mockResolvedValueOnce(Array.from({ length: 30 }, (_, index) => scan(35 - index)))
      .mockResolvedValueOnce([scan(5), scan(4), scan(3), scan(2), scan(1)])
    vi.mocked(api.scanCount).mockResolvedValue({ count: 35 })

    const wrapper = mount(ReportsView, { global: { stubs: {
      RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
      ElButton: { props: ['loading'], template: '<button class="history-load-more" :disabled="loading" @click="$emit(\'click\')"><slot /></button>' },
    } } })
    await flushPromises()

    expect(wrapper.findAll('.report-row')).toHaveLength(30)
    expect(wrapper.text()).toContain('30 / 35')
    await wrapper.find('button.history-load-more').trigger('click')
    await flushPromises()

    expect(api.scans).toHaveBeenLastCalledWith(30, 30)
    expect(wrapper.findAll('.report-row')).toHaveLength(35)
    expect(wrapper.text()).toContain('记录 1')
    expect(wrapper.find('button.history-load-more').exists()).toBe(false)
  })
})
