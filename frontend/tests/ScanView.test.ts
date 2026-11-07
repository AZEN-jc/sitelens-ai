import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ElMessage } from 'element-plus'
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
  beforeEach(() => vi.clearAllMocks())

  it('keeps scan results visible when the optional AI status request fails', async () => {
    vi.mocked(api.scan).mockResolvedValue({
      id: 42,
      url: 'https://example.test',
      final_url: 'https://example.test',
      status_code: 200,
      content_type: 'text/html',
      title: '演示站点',
      headers: {},
      created_at: '2026-11-04T00:00:00Z',
      technologies: [],
      ai_report_count: 0,
      ai_reports: [],
      scripts: [],
      styles: [],
      meta: [],
    })
    vi.mocked(api.aiStatus).mockRejectedValue(new Error('连接失败'))

    const wrapper = mount(ScanView, {
      global: {
        stubs: {
          RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('演示站点')
    expect(wrapper.text()).not.toContain('无法显示这条检测记录')
    await wrapper.findAll('button').find(button => button.text().includes('AI 分析'))?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('暂时无法读取 AI 配置状态')
    expect(wrapper.text()).not.toContain('尚未配置 AI 服务')
    expect(wrapper.find('a[href="/settings"]').exists()).toBe(false)
    expect(ElMessage.error).not.toHaveBeenCalled()
  })

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

  it('states a confirmed verdict for direct evidence and marks indirect-only hits as suspected', async () => {
    vi.mocked(api.scan).mockResolvedValue({
      id: 43,
      url: 'https://example.test',
      final_url: 'https://example.test',
      status_code: 200,
      content_type: 'text/html',
      title: '结论演示',
      headers: { server: 'BWS/1.1' },
      duration_ms: 1234,
      page_bytes: 20480,
      created_at: '2026-11-07T00:00:00Z',
      technologies: [
        { name: 'Nginx', category: 'Web server', category_label: 'Web 服务器', score: 85, confidence: 'high',
          evidence: [{ source: 'header:server', matched: 'nginx', kind: 'direct', weight: 85 }] },
        { name: 'Vue', category: 'Frontend framework', category_label: '前端框架', score: 45, confidence: 'medium',
          evidence: [{ source: 'html', matched: 'data-v-1a2b', kind: 'indirect', weight: 45 }] },
      ],
      ai_report_count: 0,
      ai_reports: [],
      scripts: [],
      styles: [],
      meta: [],
    })
    vi.mocked(api.aiStatus).mockResolvedValue({ configured: false })

    const wrapper = mount(ScanView, {
      global: {
        stubs: {
          RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
          TechnologyChart: true,
          ArchitectureGraph: true,
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('可以确认这个网站使用了：Nginx')
    expect(wrapper.text()).toContain('响应耗时')
    expect(wrapper.text()).toContain('1.23 秒')
    expect(wrapper.text()).toContain('页面大小')
    expect(wrapper.text()).toContain('20.0 KB')
    expect(wrapper.text()).toContain('服务器身份（Server）')
    expect(wrapper.text()).toContain('仅供参考')
    expect(wrapper.text()).toContain('Vue')
  })
})
