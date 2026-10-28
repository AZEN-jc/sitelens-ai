const technologyCategoryLabels: Record<string, string> = {
  Analytics: '分析统计',
  CDN: '内容分发网络',
  CMS: '内容管理系统',
  'Frontend framework': '前端框架',
  'JavaScript library': 'JavaScript 库',
  'Static site tool': '静态站点工具',
  'UI framework': 'UI 框架',
  'Web framework': 'Web 框架',
  'Web server': 'Web 服务器',
}

export function technologyCategoryLabel(category: string) {
  return technologyCategoryLabels[category] || category
}
