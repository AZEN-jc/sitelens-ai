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

  it('requires authorization before submitting the target', async () => {
    vi.mocked(api.createScan).mockResolvedValue({ id: 7 } as never)
    const wrapper = mount(ScanForm, { global: { components: { ElButton, ElInput } } })
    await wrapper.find('input[type="url"]').setValue('https://example.test')
    await wrapper.find('form').trigger('submit')
    expect(api.createScan).not.toHaveBeenCalled()

    await wrapper.find('input[type="checkbox"]').setValue(true)
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(api.createScan).toHaveBeenCalledWith('https://example.test')
    expect(router.push).toHaveBeenCalledWith('/scans/7')
  })
})
