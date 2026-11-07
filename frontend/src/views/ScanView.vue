<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api, reportUrl } from '../api'
import type { Scan } from '../types'

const TechnologyChart = defineAsyncComponent(() => import('../components/TechnologyChart.vue'))
const ArchitectureGraph = defineAsyncComponent(() => import('../components/ArchitectureGraph.vue'))
const route = useRoute()
const scan = ref<Scan | null>(null)
const loading = ref(true)
const loadError = ref('')
const activeTab = ref('overview')
const sending = ref(false)
const confirmed = ref(false)
const aiConfigured = ref<boolean | null>(null)
const aiStatusError = ref('')
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }

async function load() {
  loading.value = true
  scan.value = null
  loadError.value = ''
  aiConfigured.value = null
  aiStatusError.value = ''
  try {
    scan.value = await api.scan(String(route.params.id))
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '无法读取这条检测记录。'
    ElMessage.error(loadError.value)
    loading.value = false
    return
  }
  try {
    aiConfigured.value = (await api.aiStatus()).configured
  } catch {
    aiStatusError.value = '暂时无法读取 AI 配置状态。'
  }
  loading.value = false
}
onMounted(load)
watch(() => route.params.id, load)

const categories = computed(() => {
  const counts = new Map<string, number>()
  for (const tech of scan.value?.technologies || []) {
    const category = tech.category_label
    counts.set(category, (counts.get(category) || 0) + 1)
  }
  return [...counts].map(([name, value]) => ({ name, value }))
})
const verdict = computed(() => {
  const techs = scan.value?.technologies || []
  const hasDirect = (tech: typeof techs[number]) => tech.evidence.some(item => item.kind === 'direct')
  const confirmedList = techs.filter(hasDirect)
  const suspected = techs.filter(tech => !hasDirect(tech))
  const kind = !techs.length ? 'none' : confirmedList.length ? 'confirmed' : 'tentative'
  return { kind, confirmedList, suspected } as const
})
const aiPreview = computed(() => scan.value && ({
  url: scan.value.url,
  final_url: scan.value.final_url,
  status_code: scan.value.status_code,
  title: scan.value.title,
  technologies: scan.value.technologies.map(tech => ({
    name: tech.name, category: tech.category, confidence: tech.confidence,
    evidence: tech.evidence.map(item => ({ source: item.source, matched: item.matched })),
  })),
}))

async function analyze() {
  if (!scan.value || !confirmed.value) return
  sending.value = true
  try {
    await api.analyze(scan.value.id)
    scan.value = await api.scan(scan.value.id)
    confirmed.value = false
    ElMessage.success('AI 分析已保存到这条检测记录。')
  } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'AI 分析失败。') }
  finally { sending.value = false }
}

function openPrintReport() { window.open(reportUrl(scan.value!.id, 'html'), '_blank', 'noopener') }

const HEADER_LABELS: Record<string, string> = {
  server: '服务器身份（Server）',
  'x-powered-by': '框架标识（X-Powered-By）',
  via: '经过的代理（Via）',
  'cf-ray': 'Cloudflare 节点编号（CF-Ray）',
  'content-type': '内容类型（Content-Type）',
}
const META_LABELS: Record<string, string> = {
  generator: '页面生成器声明',
  'application-name': '应用名称',
  'og:site_name': '站点名称',
  robots: '搜索引擎抓取规则',
  viewport: '移动端适配声明',
}
const durationLabel = computed(() => {
  const value = scan.value?.duration_ms || 0
  return value > 0 ? `${(value / 1000).toFixed(2)} 秒` : ''
})
const pageSizeLabel = computed(() => {
  const value = scan.value?.page_bytes || 0
  return value > 0 ? `${(value / 1024).toFixed(1)} KB` : ''
})
const redirected = computed(() => {
  if (!scan.value) return false
  try { return new URL(scan.value.url).hostname !== new URL(scan.value.final_url).hostname } catch { return scan.value.url !== scan.value.final_url }
})
const headerRows = computed(() => Object.entries(scan.value?.headers || {}).map(([key, value]) => ({
  label: HEADER_LABELS[key] || key, value,
})))
const metaRows = computed(() => (scan.value?.meta || []).map(item => ({
  label: META_LABELS[item.name] || item.name, value: item.content,
})))
</script>

<template>
  <div v-if="loading" class="page-wrap loading-state">正在读取检测记录…</div>
  <div v-else-if="scan" class="page-wrap scan-page">
    <div class="scan-header">
      <div><div class="eyebrow">检测结果 / {{ String(scan.id).padStart(4, '0') }}</div><h1>{{ scan.title || hostOf(scan.final_url) }}</h1><a class="url-display" :href="scan.final_url" target="_blank" rel="noreferrer">{{ scan.final_url }} ↗</a></div>
      <div class="scan-actions"><span class="complete-badge"><i></i>检测完成</span><el-button @click="openPrintReport">导出报告 ↗</el-button></div>
    </div>
    <div class="result-meta"><span><small>HTTP 状态</small><b>{{ scan.status_code }}</b></span><span v-if="durationLabel"><small>响应耗时</small><b>{{ durationLabel }}</b></span><span v-if="pageSizeLabel"><small>页面大小</small><b>{{ pageSizeLabel }}</b></span><span><small>技术数量</small><b>{{ scan.technologies.length.toString().padStart(2, '0') }}</b></span><span><small>内容类型</small><b>{{ scan.content_type || '未知' }}</b></span><span><small>检测时间</small><b>{{ new Date(scan.created_at).toLocaleString('zh-CN') }}</b></span></div>
    <div v-if="redirected" class="redirect-note">访问的原地址发生了跳转，最终停在了 <code>{{ scan.final_url }}</code></div>
    <nav class="result-tabs" aria-label="检测结果分区">
      <button v-for="tab in ['overview', 'evidence', 'architecture', 'insights']" :key="tab" :class="{ selected: activeTab === tab }" @click="activeTab = tab">{{ ({ overview: '概览', evidence: '证据', architecture: '架构推测', insights: 'AI 分析' } as Record<string, string>)[tab] }}<span v-if="tab === 'insights' && scan.ai_reports.length" class="tab-count">{{ scan.ai_reports.length }}</span></button>
    </nav>

    <section v-if="activeTab === 'overview'" class="result-grid">
      <div class="result-main">
        <div v-if="verdict.kind !== 'none'" class="verdict-panel" :class="verdict.kind">
          <div class="verdict-head"><span class="verdict-tag">{{ verdict.kind === 'confirmed' ? '检测结论' : '初步发现' }}</span>
            <strong v-if="verdict.kind === 'confirmed'">可以确认这个网站使用了：{{ verdict.confirmedList.map(item => item.name).join('、') }}</strong>
            <strong v-else>没有足够把握下结论</strong>
          </div>
          <p v-if="verdict.kind === 'confirmed'">判断依据：这些技术在网站的响应头或页面声明里<em>白纸黑字</em>写明了自己的身份，就像身份证一样，不是靠猜的。<template v-if="verdict.suspected.length">另外发现了 {{ verdict.suspected.map(item => item.name).join('、') }} 的踪迹，但只是靠文件名之类的旁证推断，仅供参考。</template></p>
          <p v-else>这次发现了 {{ verdict.suspected.map(item => item.name).join('、') }} 的踪迹，但都只是文件名、页面关键字之类的旁证，可能误判，所以不下定论。</p>
        </div>
        <div class="section-title-row compact"><div><div class="eyebrow">自动比对 · 找到 {{ scan.technologies.length }} 项技术踪迹</div><h2>识别结果</h2></div><span class="confidence-note">分数越高，把握越大</span></div>
        <div v-if="scan.technologies.length" class="technology-grid">
          <article v-for="tech in scan.technologies" :key="tech.name" class="technology-card">
            <div class="tech-card-top"><span class="tech-symbol">◈</span><span class="confidence-pill" :class="tech.confidence">{{ ({ high: '高', medium: '中', low: '低' } as Record<string, string>)[tech.confidence] }}置信等级</span></div>
            <h3>{{ tech.name }}</h3><span class="tech-category">{{ tech.category_label }}</span><div class="score-track"><i :style="{ width: `${tech.score}%` }"></i></div>
            <button class="evidence-link" @click="activeTab = 'evidence'">{{ tech.evidence.length }} 条证据 <span>↗</span></button>
          </article>
        </div>
        <div v-else class="empty-state small-empty">这次没有发现任何线索。注意：没发现不等于没用——有些技术的踪迹藏在接口响应里，一次普通访问看不到。</div>
      </div>
      <aside class="result-side"><div class="side-panel"><div class="eyebrow">技术分类</div><h3>按类别统计</h3><TechnologyChart v-if="categories.length" :categories="categories" /><div v-else class="chart-empty">暂无匹配证据</div></div>
        <div class="side-panel observed-panel"><div class="eyebrow">响应中观察到的信息</div><h3>公开信号</h3><dl><dt>网页标题</dt><dd>{{ scan.title || '未提供' }}</dd><dt>JavaScript 资源</dt><dd>{{ scan.scripts.length }}</dd><dt>CSS 资源</dt><dd>{{ scan.styles.length }}</dd><dt>Meta 信息</dt><dd>{{ scan.meta.length }}</dd></dl></div>
        <div v-if="headerRows.length" class="side-panel"><div class="eyebrow">网站自己报告的身份</div><h3>响应头明细</h3><dl class="detail-list"><template v-for="row in headerRows" :key="row.label"><dt>{{ row.label }}</dt><dd><code>{{ row.value }}</code></dd></template></dl></div>
        <div v-if="metaRows.length" class="side-panel"><div class="eyebrow">页面对搜索引擎的说明</div><h3>页面声明</h3><dl class="detail-list"><template v-for="row in metaRows" :key="row.label"><dt>{{ row.label }}</dt><dd>{{ row.value }}</dd></template></dl></div>
        <details v-if="scan.scripts.length || scan.styles.length" class="side-panel resource-panel"><summary><div class="eyebrow">页面加载了哪些外部文件</div><h3>资源清单</h3></summary>
          <div v-if="scan.scripts.length" class="resource-group"><h4>脚本文件（{{ scan.scripts.length }}）</h4><ul><li v-for="item in scan.scripts.slice(0, 10)" :key="item"><code>{{ item }}</code></li></ul><p v-if="scan.scripts.length > 10" class="inline-note">其余 {{ scan.scripts.length - 10 }} 个未列出。</p></div>
          <div v-if="scan.styles.length" class="resource-group"><h4>样式表（{{ scan.styles.length }}）</h4><ul><li v-for="item in scan.styles.slice(0, 10)" :key="item"><code>{{ item }}</code></li></ul><p v-if="scan.styles.length > 10" class="inline-note">其余 {{ scan.styles.length - 10 }} 个未列出。</p></div>
        </details>
      </aside>
    </section>

    <section v-else-if="activeTab === 'evidence'" class="tab-content">
      <div class="section-title-row compact"><div><div class="eyebrow">追溯每一条匹配</div><h2>识别证据</h2></div></div>
      <article v-for="tech in scan.technologies" :key="tech.name" class="evidence-card"><div class="evidence-heading"><span class="tech-symbol">◈</span><div><h3>{{ tech.name }}</h3><span>{{ tech.category_label }} · {{ ({ high: '高', medium: '中', low: '低' } as Record<string, string>)[tech.confidence] }}置信等级 · 评分 {{ tech.score }}/100</span></div></div><div v-for="item in tech.evidence" :key="`${item.source}-${item.matched}`" class="evidence-row"><span class="evidence-kind" :class="item.kind">{{ item.kind === 'direct' ? '白纸黑字' : '旁证推断' }}</span><code>{{ item.source }}</code><p>{{ item.matched }}</p><small>权重 {{ item.weight }}</small></div></article>
      <div v-if="!scan.technologies.length" class="empty-state">没有匹配到证据。</div>
    </section>

    <section v-else-if="activeTab === 'architecture'" class="tab-content"><div class="section-title-row compact"><div><div class="eyebrow">推测的技术关系</div><h2>架构关系图</h2></div><span class="confidence-note">根据公开信号推测，不代表已证实的内部部署情况。</span></div>
      <ArchitectureGraph :technologies="scan.technologies" />
      <p class="method-note">连线表示这些技术在同一次公开响应中被观察到。本工具无法看到网站的内部请求路径或部署拓扑。</p>
    </section>

    <section v-else class="tab-content ai-tab"><div class="section-title-row compact"><div><div class="eyebrow">AI 辅助解读</div><h2>技术分析</h2></div><RouterLink v-if="aiConfigured === false" to="/settings" class="text-link">配置 AI ↗</RouterLink></div>
      <div v-if="scan.ai_reports.length" class="ai-report-list"><article v-for="report in scan.ai_reports" :key="report.id" class="ai-report"><div class="ai-report-meta"><span>模型 / {{ report.model }}</span><time>{{ new Date(report.created_at).toLocaleString('zh-CN') }}</time></div><p>{{ report.content }}</p></article></div>
      <div class="ai-compose"><div class="ai-compose-head"><span class="ai-spark">✳</span><div><h3>基于证据生成分析</h3><p>AI 只接收本次检测摘要和匹配到的证据，不负责判断某项技术是否存在。</p></div></div>
        <details v-if="aiPreview" class="data-preview"><summary>查看即将发送的具体数据</summary><pre>{{ JSON.stringify(aiPreview, null, 2) }}</pre></details>
        <label class="authorization ai-confirm"><input v-model="confirmed" type="checkbox" /> 我已了解：这些摘要信息将发送到我配置的 AI 服务。</label>
        <el-button type="primary" :loading="sending" :disabled="aiConfigured !== true || !confirmed" @click="analyze">{{ scan.ai_reports.length ? '再生成一份分析' : '生成 AI 分析' }} ↗</el-button>
        <p v-if="aiConfigured === false" class="inline-note">尚未配置 AI 服务。请先前往“设置”添加兼容接口。</p>
        <p v-else-if="aiStatusError" class="inline-note">{{ aiStatusError }}</p>
      </div>
    </section>
    <footer class="page-footer"><span>检测记录 {{ String(scan.id).padStart(4, '0') }}</span><span>本次未观察到证据，不代表技术已被移除。</span><a :href="reportUrl(scan.id, 'json')" target="_blank" rel="noreferrer">下载 JSON ↗</a></footer>
  </div>
  <div v-else class="page-wrap">
    <div class="empty-state scan-load-error" role="alert">
      <span class="empty-symbol">!</span>
      <b>无法显示这条检测记录</b>
      <span>{{ loadError || '这条记录可能不存在，或本机服务暂时无法读取它。' }}</span>
      <RouterLink to="/" class="text-link">返回概览 ↗</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.verdict-panel {
  border: 1px solid #2a2a2a;
  border-left: 3px solid var(--alert, #e61919);
  background: #141414;
  padding: 14px 16px;
  margin-bottom: 18px;
}
.verdict-panel.tentative { border-left-color: #8a8a8a; }
.verdict-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.verdict-tag {
  font-size: 11px; letter-spacing: .08em; padding: 2px 8px;
  border: 1px solid var(--alert, #e61919); color: var(--alert, #e61919); white-space: nowrap;
}
.verdict-panel.tentative .verdict-tag { border-color: #8a8a8a; color: #8a8a8a; }
.verdict-head strong { font-size: 14px; color: #eaeaea; }
.verdict-panel p { margin: 8px 0 0; font-size: 12px; line-height: 1.7; color: #9a9a9a; }

.detail-list dt { margin-top: 8px; }
.detail-list dd { margin: 2px 0 0; word-break: break-all; }
.detail-list dd code { font-size: 11px; color: #d0d0d0; }
.redirect-note { margin: 10px 0 0; font-size: 12px; color: #9a9a9a; }
.redirect-note code { color: #d0d0d0; }
.resource-panel summary { cursor: pointer; list-style: none; }
.resource-panel summary::-webkit-details-marker { display: none; }
.resource-panel summary h3 { display: inline; margin-left: 8px; }
.resource-group h4 { margin: 12px 0 6px; font-size: 12px; color: #9a9a9a; font-weight: 500; }
.resource-group ul { margin: 0; padding: 0; list-style: none; }
.resource-group li { margin: 4px 0; }
.resource-group code { font-size: 11px; color: #d0d0d0; word-break: break-all; }
</style>
