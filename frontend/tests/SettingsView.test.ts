import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import SettingsView from '../src/views/SettingsView.vue'
import { api } from '../src/api'

vi.mock('../src/api', () => ({ api: {
  aiStatus: vi.fn(), configureAI: vi.fn(), testAI: vi.fn(), clearAI: vi.fn(),
} }))
vi.mock('element-plus', () => ({ ElMessage: { success: vi.fn(), error: vi.fn() } }))

describe('SettingsView', () => {
  it('saves configuration, shows a failed connection test, and clears it', async () => {
    vi.mocked(api.aiStatus)
      .mockResolvedValueOnce({ configured: false })
      .mockResolvedValueOnce({ configured: true, base_url: 'http://127.0.0.1:11434/v1', model: 'local' })
      .mockResolvedValueOnce({ configured: false })
    vi.mocked(api.configureAI).mockResolvedValue({ configured: true })
    vi.mocked(api.testAI).mockResolvedValue({ ok: false, error: '服务不可用' })
    vi.mocked(api.clearAI).mockResolvedValue(undefined)

    const wrapper = mount(SettingsView, { global: { stubs: {
      ElInput: {
        props: ['modelValue', 'type'], emits: ['update:modelValue'],
        template: '<input :type="type || \'text\'" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
      },
      ElButton: {
        props: ['nativeType', 'disabled', 'loading'], emits: ['click'],
        template: '<button :type="nativeType || \'button\'" :disabled="disabled || loading" @click="$emit(\'click\')"><slot /></button>',
      },
    } } })
    await flushPromises()

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('http://127.0.0.1:11434/v1')
    await inputs[1].setValue('local')
    await inputs[2].setValue('test-secret-123')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(api.configureAI).toHaveBeenCalledWith('http://127.0.0.1:11434/v1', 'test-secret-123', 'local')
    expect((inputs[2].element as HTMLInputElement).value).toBe('')
    expect(wrapper.text()).toContain('已配置')

    await wrapper.findAll('button').find(button => button.text().includes('测试连接'))!.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('服务不可用')

    await wrapper.findAll('button').find(button => button.text().includes('清除配置'))!.trigger('click')
    await flushPromises()
    expect(api.clearAI).toHaveBeenCalledOnce()
    expect(wrapper.text()).toContain('未连接')
  })
})
