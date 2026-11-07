import { flushPromises, mount } from '@vue/test-utils'
import { ElButton, ElInput } from 'element-plus'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ScanForm from '../src/components/ScanForm.vue'
import { api } from '../src/api'
import { router } from '../src/router'

vi.mock('../src/api', () => ({ api: { createScan: vi.fn() } }))
vi.mock('../src/router', () => ({ router: { push: vi.fn() } }))

describe('ScanForm', () => {
  beforeEach(() => vi.clearAllMocks())

  it('submits a bare domain and navigates to the scan', async () => {
    vi.mocked(api.createScan).mockResolvedValue({ id: 7 } as never)
    const wrapper = mount(ScanForm, { global: { components: { ElButton, ElInput } } })
    await wrapper.find('input[type="text"]').setValue('example.test')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(api.createScan).toHaveBeenCalledWith('example.test')
    expect(router.push).toHaveBeenCalledWith('/scans/7')
  })

  it('does not call the api when the url is empty', async () => {
    const wrapper = mount(ScanForm, { global: { components: { ElButton, ElInput } } })
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(api.createScan).not.toHaveBeenCalled()
    expect(router.push).not.toHaveBeenCalled()
  })
})
