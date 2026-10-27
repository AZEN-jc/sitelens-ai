import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import App from '../src/App.vue'
import { router } from '../src/router'

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return { ...actual, useRoute: () => ({ path: '/' }) }
})

describe('app navigation', () => {
  it('shows a Chinese settings link in the main navigation', () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
          RouterView: true,
        },
      },
    })

    const settingsLink = wrapper.find('.side-nav a[href="/settings"]')
    expect(settingsLink.exists()).toBe(true)
    expect(settingsLink.text()).toContain('设置')
    expect(router.resolve('/settings').matched).toHaveLength(1)
  })
})
