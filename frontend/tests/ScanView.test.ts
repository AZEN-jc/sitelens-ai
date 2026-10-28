import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import ScanView from '../src/views/ScanView.vue'
import { api } from '../src/api'

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return {
    ...actual,
    useRoute: () => ({ params: { id: '999999' } }),
  }
})

vi.mock('../src/api', () => ({
  api: { scan: vi.fn(), aiStatus: vi.fn(), analyze: vi.fn() },
  reportUrl: (id: number, format: string) => `/api/reports/${id}/export?format=${format}`,
}))

vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
}))

describe('ScanView', () => {
  it('shows a Chinese error state when the scan record cannot be loaded', async () => {
    vi.mocked(api.scan).mockRejectedValue(new Error('未找到这条检测记录。'))

    const wrapper = mount(ScanView, {
      global: {
        stubs: {
          RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('无法显示这条检测记录')
    expect(wrapper.text()).toContain('未找到这条检测记录。')
    expect(wrapper.find('a[href="/"]').text()).toContain('返回概览')
    expect(api.aiStatus).not.toHaveBeenCalled()
  })
})
