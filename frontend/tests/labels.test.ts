import { describe, expect, it } from 'vitest'
import { technologyCategoryLabel } from '../src/labels'

describe('technologyCategoryLabel', () => {
  it('localizes built-in detector categories and preserves unknown values', () => {
    expect(technologyCategoryLabel('Frontend framework')).toBe('前端框架')
    expect(technologyCategoryLabel('Web server')).toBe('Web 服务器')
    expect(technologyCategoryLabel('CMS')).toBe('内容管理系统')
    expect(technologyCategoryLabel('Custom category')).toBe('Custom category')
  })
})
