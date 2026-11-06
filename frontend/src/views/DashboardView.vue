<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { RouterLink } from 'vue-router'
import { api } from '../api'
import ScanForm from '../components/ScanForm.vue'
import type { Scan } from '../types'

type TabKey = 'overview' | 'evidence'

const FALLBACK: Scan[] = [
  {
    id: 3, url: 'https://react.demo.test/', final_url: 'https://react.demo.test/',
    status_code: 200, content_type: 'text/html; charset=utf-8', title: '示例站点 · React 技术演示',
    headers: {}, meta: [], scripts: [], styles: [], created_at: '2026-11-05T12:00:00Z',
    ai_report_count: 0, ai_reports: [],
    technologies: [
      { name: 'React', category: 'Frontend framework', category_label: '前端框架', score: 100, confidence: 'high', evidence: [
        { source: 'html', matched: 'data-reactroot', kind: 'indirect', weight: 70 },
        { source: 'script_src', matched: '/assets/react-dom.js', kind: 'indirect', weight: 60 },
      ] },
      { name: 'Nginx', category: 'Web server', category_label: 'Web 服务器', score: 85, confidence: 'high', evidence: [
        { source: 'header:server', matched: 'nginx', kind: 'direct', weight: 85 },
      ] },
    ],
  },
  {
    id: 2, url: 'https://wordpress.demo.test/', final_url: 'https://wordpress.demo.test/',
    status_code: 200, content_type: 'text/html; charset=utf-8', title: '示例站点 · WordPress 技术演示',
    headers: {}, meta: [], scripts: [], styles: [], created_at: '2026-11-05T11:00:00Z',
    ai_report_count: 0, ai_reports: [],
    technologies: [
      { name: 'WordPress', category: 'CMS', category_label: '内容管理系统', score: 100, confidence: 'high', evidence: [
        { source: 'meta_generator', matched: 'WordPress 6.8', kind: 'direct', weight: 90 },
        { source: 'style_href', matched: '/wp-content/themes/demo/style.css', kind: 'indirect', weight: 60 },
      ] },
      { name: 'Apache', category: 'Web server', category_label: 'Web 服务器', score: 85, confidence: 'high', evidence: [
        { source: 'header:server', matched: 'Apache', kind: 'direct', weight: 85 },
      ] },
    ],
  },
]

const scans = ref<Scan[]>([])
const totalScans = ref(0)
const loading = ref(true)
const source = ref<'实时接口' | '离线样本'>('离线样本')
const activeTab = ref<TabKey>('overview')
const expanded = ref<number | null>(null)
const tabs: { key: TabKey; label: string }[] = [
  { key: 'overview', label: '识别概览' },
  { key: 'evidence', label: '命中证据' },
]

onMounted(async () => {
  try {
    const [recent, count] = await Promise.all([api.scans(8), api.scanCount()])
    scans.value = recent
    totalScans.value = count.count
    source.value = '实时接口'
  } catch (error) {
    scans.value = FALLBACK
    totalScans.value = FALLBACK.length
    source.value = '离线样本'
    ElMessage.error(error instanceof Error ? `实时数据不可用，已显示内置样本。${error.message}` : '实时数据不可用，已显示内置样本。')
  } finally {
    loading.value = false
  }
})

const displayScans = computed(() => scans.value.length ? scans.value : FALLBACK)
const focusScan = computed(() => displayScans.value.find(scan => scan.technologies.length) ?? displayScans.value[0] ?? FALLBACK[0])
const technologies = computed(() => focusScan.value?.technologies ?? [])
const evidenceCount = computed(() => technologies.value.reduce((sum, item) => sum + item.evidence.length, 0))
const totalEvidence = computed(() => displayScans.value.reduce((sum, scan) => sum + scan.technologies.reduce((n, item) => n + item.evidence.length, 0), 0))
const uniqueTech = computed(() => new Set(displayScans.value.flatMap(scan => scan.technologies.map(item => item.name))).size)

function selectTab(key: TabKey) { activeTab.value = key }
function onTabKey(event: KeyboardEvent, index: number) {
  if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return
  event.preventDefault()
  const next = (index + (event.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length
  selectTab(tabs[next].key)
  document.getElementById('tab-' + tabs[next].key)?.focus()
}
function toggle(index: number) { expanded.value = expanded.value === index ? null : index }
function date(value: string) { return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) }
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
function level(value: string) { return ({ high: '高', medium: '中', low: '低' } as Record<string, string>)[value] ?? value }
</script>

<template>
  <div class="page-wrap tactical">
    <header class="tac-hero">
      <div class="tac-eyebrow"><span class="cross">+</span><span>版本 2026.11</span><i></i><span>单元 SL-01</span><i></i><span>本机运行 · 数据不出设备</span></div>
      <h1 class="tac-title">网站技术<span>识别与分析</span></h1>
      <p class="tac-sub">&gt;&gt;&gt; 基于公开证据 · 每项识别都可追溯</p>
      <p class="tac-lede">用一次普通公开请求还原网站的技术栈。每一项识别都列出命中的响应证据，AI 只解释观测结果，不参与判定。系统在本机运行，不需要账号，也不上传数据。</p>
      <div class="tac-cta">
        <a class="tac-btn primary" href="#detection">查看检测结果 <span>↓</span></a>
        <RouterLink class="tac-btn" to="/compare">对比历史记录 <span>→</span></RouterLink>
      </div>
    </header>

    <section class="tac-readouts" aria-label="系统遥测">
      <div class="readout"><span class="label">检测次数</span><strong>{{ totalScans.toString().padStart(2, '0') }}</strong></div>
      <div class="readout"><span class="label">识别技术</span><strong class="accent">{{ uniqueTech.toString().padStart(2, '0') }}</strong></div>
      <div class="readout"><span class="label">证据字段</span><strong>{{ totalEvidence.toString().padStart(2, '0') }}</strong></div>
      <div class="readout"><span class="label">数据来源</span><strong class="small">{{ source }}</strong></div>
    </section>

    <section class="tac-block">
      <div class="tac-head"><span><b>[ 01 ] 新建检测</b> · 输入网址开始</span><span class="hint">仅采集公开信息 · 需勾选授权</span></div>
      <div class="tac-scan"><ScanForm /></div>
    </section>

    <section id="detection" class="tac-block">
      <div class="tac-head"><span><b>[ 02 ] 识别结果</b> · {{ focusScan?.title || '演示样本' }}</span><span class="hint">点击任意一行，展开命中证据 ↓</span></div>
      <div class="tac-tabs" role="tablist" aria-label="检测结果视图">
        <button v-for="(tab, index) in tabs" :key="tab.key" :id="'tab-' + tab.key" role="tab" type="button"
          :aria-selected="activeTab === tab.key" :tabindex="activeTab === tab.key ? 0 : -1"
          @click="selectTab(tab.key)" @keydown="onTabKey($event, index)">
          <span>{{ tab.label }}</span><small>{{ String(index + 1).padStart(2, '0') }}</small>
        </button>
      </div>

      <div v-if="activeTab === 'overview'" class="tac-pane" role="tabpanel">
        <div class="tac-meta"><span>目标：{{ focusScan?.final_url }}</span><span>状态码 {{ focusScan?.status_code }}</span><span>引擎：指纹规则</span></div>
        <div v-if="technologies.length" class="tech-list">
          <div v-for="(tech, index) in technologies" :key="tech.name" class="tech-row">
            <button class="tech-trigger" type="button" :aria-expanded="expanded === index" :aria-controls="'ev-' + index" @click="toggle(index)">
              <span class="num">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="tech-name">{{ tech.name }}</span>
              <span class="tech-cat">{{ tech.category_label }}</span>
              <span class="tech-score">{{ tech.score }} / {{ level(tech.confidence) }}</span>
              <span class="chev" :class="{ open: expanded === index }">›</span>
            </button>
            <div v-if="expanded === index" :id="'ev-' + index" class="evidence-box">
              <div v-for="(item, i) in tech.evidence" :key="i" class="evidence-line">
                <span class="src">{{ item.source }}</span><span class="matched">{{ item.matched }}</span><span class="w">+{{ item.weight }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="tac-empty">[ 未命中 ] 本次响应没有命中已知指纹。这不代表目标没有使用相关技术。</div>
      </div>

      <div v-else-if="activeTab === 'evidence'" class="tac-pane" role="tabpanel">
        <div class="tac-meta"><span>每条技术都绑定命中的公开响应字段</span><span>共 {{ evidenceCount }} 条</span></div>
        <article v-for="tech in technologies" :key="tech.name" class="trace-group">
          <div class="tac-meta"><span class="accent">[ {{ tech.name.toUpperCase() }} ]</span><span>{{ level(tech.confidence) }} / {{ tech.score }}</span></div>
          <div v-for="(item, i) in tech.evidence" :key="i" class="evidence-line">
            <span class="src">{{ item.source }}</span><span class="matched">{{ item.matched }}</span><span class="w">+{{ item.weight }}</span>
          </div>
        </article>
        <div v-if="!technologies.length" class="tac-empty">[ 暂无证据 ] 本次没有可追溯的命中字段。</div>
      </div>

    </section>

    <section class="tac-block">
      <div class="tac-head"><span><b>[ 03 ] 最近记录</b></span><span class="hint">每一行都可点击 →</span></div>
      <div v-if="loading" class="tac-empty">[ 读取中 ] 正在读取本机历史记录…</div>
      <div v-else-if="!displayScans.length" class="tac-empty">[ 暂无记录 ] 完成第一次授权检测后，结果会显示在这里。</div>
      <div v-else class="index-list">
        <RouterLink v-for="(scan, index) in displayScans.slice(0, 8)" :key="scan.id" :to="`/scans/${scan.id}`" class="index-row">
          <span class="num">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="row-title">{{ scan.title || hostOf(scan.final_url) }}</span>
          <span class="row-note">{{ scan.technologies.length }} 项技术 · {{ date(scan.created_at) }}</span>
          <span class="go">→</span>
        </RouterLink>
      </div>
    </section>

    <footer class="page-footer"><span>毕业设计作品 · 本机演示</span><span>识别结果由公开证据支持；架构关系仅为推测。</span><span>无需账号 · 数据不上传</span></footer>
  </div>
</template>

<style scoped>
.tactical { font-family: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "PingFang SC", "Microsoft YaHei", monospace; }
.tac-hero { padding: 46px 0 44px; border-bottom: 1px solid #333; }
.tac-eyebrow { display: flex; flex-wrap: wrap; gap: 8px 18px; align-items: center; font-size: 10px; letter-spacing: .1em; color: #8a8a8a; text-transform: uppercase; }
.tac-eyebrow .cross { color: var(--alert); font-size: 15px; line-height: 1; }
.tac-eyebrow i { width: 24px; height: 1px; background: #3a3a3a; }
.tac-title { margin: 34px 0 14px; font-size: clamp(44px, 7.5vw, 104px); font-weight: 800; line-height: 1.08; letter-spacing: -.04em; color: #eaeaea; }
.tac-title span { display: block; color: #9a9a9a; font-weight: 500; }
.tac-sub { margin: 0 0 20px; font-size: 11px; letter-spacing: .1em; color: var(--alert); }
.tac-lede { max-width: 62ch; margin: 0 0 30px; font-size: 13px; line-height: 1.7; color: #9a9a9a; text-wrap: pretty; }
.tac-cta { display: flex; flex-wrap: wrap; gap: 10px; }
.tac-btn { display: inline-flex; align-items: center; gap: 12px; padding: 13px 20px; border: 1px solid #3a3a3a; background: transparent; color: #eaeaea; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-decoration: none; cursor: pointer; transition: background .2s, color .2s, border-color .2s, transform .12s; }
.tac-btn:hover { border-color: var(--alert); color: var(--alert); background: #161616; }
.tac-btn:active { transform: translateY(1px); }
.tac-btn.primary { background: var(--alert); border-color: var(--alert); color: #0a0a0a; }
.tac-btn.primary:hover { filter: brightness(1.15); color: #0a0a0a; }
:focus-visible { outline: 2px solid var(--alert); outline-offset: 3px; }

.tac-readouts { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: #2a2a2a; border: 1px solid #2a2a2a; margin: 22px 0 34px; }
.readout { background: #0a0a0a; padding: 18px 20px; min-height: 104px; display: flex; flex-direction: column; justify-content: space-between; }
.readout .label { font-size: 9.5px; letter-spacing: .1em; color: #8a8a8a; }
.readout strong { font-size: clamp(26px, 3vw, 40px); font-weight: 700; letter-spacing: -.04em; line-height: 1; font-variant-numeric: tabular-nums; }
.readout strong.accent { color: var(--alert); }
.readout strong.small { font-size: 14px; letter-spacing: .04em; }

.tac-block { margin-bottom: 34px; }
.tac-head { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 12px; padding: 14px 0; border-bottom: 1px solid #2a2a2a; font-size: 10.5px; letter-spacing: .08em; color: #8a8a8a; }
.tac-head b { color: #eaeaea; font-weight: 700; }
.tac-head .hint { color: var(--alert); }
.tac-scan { padding: 20px 22px; border: 1px solid #2a2a2a; border-top: 0; background: #101010; }

.tac-tabs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; background: #2a2a2a; border: 1px solid #2a2a2a; border-top: 0; }
.tac-tabs button { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 14px 18px; border: 0; border-bottom: 2px solid transparent; background: #0a0a0a; color: #8a8a8a; font-size: 10.5px; letter-spacing: .06em; cursor: pointer; text-align: left; transition: background .2s, color .2s, border-color .2s; }
.tac-tabs button:hover { background: #161616; color: #eaeaea; }
.tac-tabs button[aria-selected="true"] { background: #161616; color: var(--alert); border-bottom-color: var(--alert); }
.tac-tabs button small { opacity: .6; }
.tac-pane { padding: 22px 24px 26px; border: 1px solid #2a2a2a; border-top: 0; background: #0d0d0d; }
.tac-meta { display: flex; flex-wrap: wrap; gap: 6px 22px; margin-bottom: 18px; font-size: 10px; letter-spacing: .08em; color: #8a8a8a; }
.tac-meta .accent { color: var(--alert); }
.tac-empty { padding: 22px; border: 1px dashed #3a3a3a; color: #8a8a8a; font-size: 11px; letter-spacing: .06em; }

.tech-row { border-top: 1px solid #2a2a2a; }
.tech-row:last-child { border-bottom: 1px solid #2a2a2a; }
.tech-trigger { display: grid; grid-template-columns: 34px minmax(0, 1fr) 150px 110px 20px; align-items: center; gap: 14px; width: 100%; padding: 14px 4px; border: 0; background: transparent; color: #eaeaea; cursor: pointer; text-align: left; transition: background .2s, padding .2s, color .2s; }
.tech-trigger:hover { background: #161616; padding-left: 12px; color: var(--alert); }
.tech-trigger:active { transform: translateY(1px); }
.tech-trigger .num, .tech-cat, .tech-score { font-size: 10px; letter-spacing: .06em; color: #8a8a8a; }
.tech-trigger:hover .num, .tech-trigger:hover .tech-cat, .tech-trigger:hover .tech-score { color: #c8c8c8; }
.tech-name { font-size: 17px; font-weight: 700; letter-spacing: -.02em; }
.tech-score { text-align: right; font-variant-numeric: tabular-nums; }
.chev { color: var(--alert); font-size: 16px; transition: transform .2s; }
.chev.open { transform: rotate(90deg); }
.evidence-box { padding: 2px 4px 18px 48px; }
.evidence-line { display: grid; grid-template-columns: 140px minmax(0, 1fr) 56px; gap: 14px; padding: 9px 0; border-top: 1px dashed #2a2a2a; font-size: 10.5px; color: #c8c8c8; }
.evidence-line .src { color: var(--alert); }
.evidence-line .w { text-align: right; color: #8a8a8a; font-variant-numeric: tabular-nums; }
.trace-group { margin-bottom: 20px; }
.trace-group .tac-meta { margin-bottom: 8px; }

.index-list { border-bottom: 1px solid #2a2a2a; }
.index-row { display: grid; grid-template-columns: 54px minmax(0, 1fr) 260px 24px; align-items: center; gap: 18px; padding: 20px 8px; border-bottom: 1px solid #2a2a2a; text-decoration: none; color: inherit; transition: background .2s, padding .2s; }
.index-row:last-child { border-bottom: 0; }
.index-row:hover { background: #161616; padding-left: 16px; }
.index-row:active { transform: translateY(1px); }
.index-row .num { font-size: 10px; color: #8a8a8a; letter-spacing: .1em; }
.index-row:hover .num { color: var(--alert); }
.row-title { font-size: 18px; font-weight: 600; letter-spacing: -.02em; }
.row-note { font-size: 10px; color: #8a8a8a; letter-spacing: .06em; }
.index-row .go { text-align: right; color: #8a8a8a; transition: color .2s, transform .2s; }
.index-row:hover .go { color: var(--alert); transform: translateX(4px); }

@media (max-width: 900px) {
  .tac-readouts { grid-template-columns: 1fr 1fr; }
  .tech-trigger { grid-template-columns: 28px 1fr 90px 18px; gap: 8px; }
  .tech-cat { display: none; }
  .index-row { grid-template-columns: 40px 1fr 20px; gap: 10px; }
  .row-note { grid-column: 2; grid-row: 2; }
  .index-row .go { grid-column: 3; grid-row: 1; }
}
@media (max-width: 560px) {
  .tac-hero { padding: 30px 0; }
  .tac-tabs { grid-template-columns: 1fr; }
  .tac-pane { padding: 18px 16px; }
  .evidence-line { grid-template-columns: 100px 1fr; }
  .evidence-line .w { display: none; }
  .evidence-box { padding-left: 20px; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: .01ms !important; }
}
</style>
