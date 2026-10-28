import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import CompareView from '../src/views/CompareView.vue'
import { api } from '../src/api'
import type { Scan } from '../src/types'

vi.mock('../src/api', () => ({ api: {
  scans: vi.fn(), scanCount: vi.fn(), compare: vi.fn(),
} }))

function scan(id: number): Scan {
  return {
    id, url: `https://example.test/${id}`, final_url: `https://example.test/${id}`,
    status_code: 200, content_type: 'text/html', title: `记录 ${id}`, headers: {}, meta: [],
    scripts: [], styles: [], created_at: '2026-10-01T00:00:00Z', technologies: [],
    ai_report_count: 0, ai_reports: [],
  }
}

describe('CompareView history paging', () => {
  it('adds older scans to both comparison selectors', async () => {
    vi.mocked(api.scans)
      .mockResolvedValueOnce(Array.from({ length: 30 }, (_, index) => scan(35 - index)))
      .mockResolvedValueOnce([scan(5), scan(4), scan(3), scan(2), scan(1)])
    vi.mocked(api.scanCount).mockResolvedValue({ count: 35 })

    const wrapper = mount(CompareView, { global: { stubs: {
      ElSelect: { template: '<div class="scan-select"><slot /></div>' },
      ElOption: { props: ['label', 'value'], template: '<option :value="value">{{ label }}</option>' },
      ElButton: {
        props: ['loading', 'disabled'], emits: ['click'],
        template: '<button class="history-load-more" :disabled="loading || disabled" @click="$emit(\'click\')"><slot /></button>',
      },
    } } })
    await flushPromises()

    expect(wrapper.findAll('.scan-select')[0].findAll('option')).toHaveLength(30)
    await wrapper.findAll('button').at(1)!.trigger('click')
    await flushPromises()

    expect(api.scans).toHaveBeenLastCalledWith(30, 30)
    expect(wrapper.findAll('.scan-select')[0].findAll('option')).toHaveLength(35)
    expect(wrapper.findAll('.scan-select')[0].text()).toContain('记录 1')
  })
})
