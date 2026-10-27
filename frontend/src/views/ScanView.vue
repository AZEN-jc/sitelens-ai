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
const activeTab = ref('overview')
const sending = ref(false)
const confirmed = ref(false)
const aiConfigured = ref(false)
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }

async function load() {
  loading.value = true
  try {
    scan.value = await api.scan(String(route.params.id))
    aiConfigured.value = (await api.aiStatus()).configured
  } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Could not load this analysis.') }
  finally { loading.value = false }
}
onMounted(load)
watch(() => route.params.id, load)

const categories = computed(() => {
  const counts = new Map<string, number>()
  for (const tech of scan.value?.technologies || []) counts.set(tech.category, (counts.get(tech.category) || 0) + 1)
  return [...counts].map(([name, value]) => ({ name, value }))
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
    ElMessage.success('Analysis saved to this scan.')
  } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'AI analysis failed.') }
  finally { sending.value = false }
}

function openPrintReport() { window.open(reportUrl(scan.value!.id, 'html'), '_blank', 'noopener') }
</script>

<template>
  <div v-if="loading" class="page-wrap loading-state">Retrieving saved analysis…</div>
  <div v-else-if="scan" class="page-wrap scan-page">
    <div class="scan-header">
      <div><div class="eyebrow">ANALYSIS / {{ String(scan.id).padStart(4, '0') }}</div><h1>{{ scan.title || hostOf(scan.final_url) }}</h1><a class="url-display" :href="scan.final_url" target="_blank" rel="noreferrer">{{ scan.final_url }} ↗</a></div>
      <div class="scan-actions"><span class="complete-badge"><i></i> ANALYSIS COMPLETE</span><el-button @click="openPrintReport">Export report ↗</el-button></div>
    </div>
    <div class="result-meta"><span><small>HTTP STATUS</small><b>{{ scan.status_code }}</b></span><span><small>TECHNOLOGIES</small><b>{{ scan.technologies.length.toString().padStart(2, '0') }}</b></span><span><small>CONTENT TYPE</small><b>{{ scan.content_type || 'Unknown' }}</b></span><span><small>CAPTURED</small><b>{{ new Date(scan.created_at).toLocaleString() }}</b></span></div>
    <nav class="result-tabs" aria-label="Analysis sections">
      <button v-for="tab in ['overview', 'evidence', 'architecture', 'insights']" :key="tab" :class="{ selected: activeTab === tab }" @click="activeTab = tab">{{ tab === 'insights' ? 'AI insights' : tab[0].toUpperCase() + tab.slice(1) }}<span v-if="tab === 'insights' && scan.ai_reports.length" class="tab-count">{{ scan.ai_reports.length }}</span></button>
    </nav>

    <section v-if="activeTab === 'overview'" class="result-grid">
      <div class="result-main"><div class="section-title-row compact"><div><div class="eyebrow">RULE ENGINE · {{ scan.technologies.length }} MATCHES</div><h2>Detected technologies</h2></div><span class="confidence-note">Confidence is an internal rule score</span></div>
        <div v-if="scan.technologies.length" class="technology-grid">
          <article v-for="tech in scan.technologies" :key="tech.name" class="technology-card">
            <div class="tech-card-top"><span class="tech-symbol">◈</span><span class="confidence-pill" :class="tech.confidence">{{ tech.confidence }} confidence</span></div>
            <h3>{{ tech.name }}</h3><span class="tech-category">{{ tech.category }}</span><div class="score-track"><i :style="{ width: `${tech.score}%` }"></i></div>
            <button class="evidence-link" @click="activeTab = 'evidence'">{{ tech.evidence.length }} evidence signals <span>↗</span></button>
          </article>
        </div>
        <div v-else class="empty-state small-empty">No known fingerprints matched this response. That does not mean the site uses no web technology.</div>
      </div>
      <aside class="result-side"><div class="side-panel"><div class="eyebrow">TECHNOLOGY MIX</div><h3>By category</h3><TechnologyChart v-if="categories.length" :categories="categories" /><div v-else class="chart-empty">No matched signals</div></div>
        <div class="side-panel observed-panel"><div class="eyebrow">OBSERVED RESPONSE</div><h3>Public signals</h3><dl><dt>Page title</dt><dd>{{ scan.title || 'Not present' }}</dd><dt>JavaScript resources</dt><dd>{{ scan.scripts.length }}</dd><dt>CSS resources</dt><dd>{{ scan.styles.length }}</dd><dt>Meta signals</dt><dd>{{ scan.meta.length }}</dd></dl></div>
      </aside>
    </section>

    <section v-else-if="activeTab === 'evidence'" class="tab-content">
      <div class="section-title-row compact"><div><div class="eyebrow">TRACE EVERY MATCH</div><h2>Evidence explorer</h2></div></div>
      <article v-for="tech in scan.technologies" :key="tech.name" class="evidence-card"><div class="evidence-heading"><span class="tech-symbol">◈</span><div><h3>{{ tech.name }}</h3><span>{{ tech.category }} · {{ tech.confidence }} · score {{ tech.score }}/100</span></div></div><div v-for="item in tech.evidence" :key="`${item.source}-${item.matched}`" class="evidence-row"><span class="evidence-kind" :class="item.kind">{{ item.kind }}</span><code>{{ item.source }}</code><p>{{ item.matched }}</p><small>weight {{ item.weight }}</small></div></article>
      <div v-if="!scan.technologies.length" class="empty-state">No evidence was matched.</div>
    </section>

    <section v-else-if="activeTab === 'architecture'" class="tab-content"><div class="section-title-row compact"><div><div class="eyebrow">INFERRED RELATIONSHIPS</div><h2>Architecture map</h2></div><span class="confidence-note">Hypothesis based on public signals — not proof of internal deployment.</span></div>
      <ArchitectureGraph :technologies="scan.technologies" />
      <p class="method-note">Connections show technologies observed in the same public response. The site’s internal request path and deployment topology are not visible to this tool.</p>
    </section>

    <section v-else class="tab-content ai-tab"><div class="section-title-row compact"><div><div class="eyebrow">AI-ASSISTED INTERPRETATION</div><h2>Technology insights</h2></div><RouterLink v-if="!aiConfigured" to="/settings" class="text-link">Configure AI ↗</RouterLink></div>
      <div v-if="scan.ai_reports.length" class="ai-report-list"><article v-for="report in scan.ai_reports" :key="report.id" class="ai-report"><div class="ai-report-meta"><span>MODEL / {{ report.model }}</span><time>{{ new Date(report.created_at).toLocaleString() }}</time></div><p>{{ report.content }}</p></article></div>
      <div class="ai-compose"><div class="ai-compose-head"><span class="ai-spark">✳</span><div><h3>Generate an evidence-based analysis</h3><p>The AI receives only this scan summary and matched evidence. It does not decide whether a technology is present.</p></div></div>
        <details v-if="aiPreview" class="data-preview"><summary>Review the exact data to be sent</summary><pre>{{ JSON.stringify(aiPreview, null, 2) }}</pre></details>
        <label class="authorization ai-confirm"><input v-model="confirmed" type="checkbox" /> I understand this summary will be sent to my configured AI service.</label>
        <el-button type="primary" :loading="sending" :disabled="!aiConfigured || !confirmed" @click="analyze">{{ scan.ai_reports.length ? 'Generate another analysis' : 'Generate AI analysis' }} ↗</el-button>
        <p v-if="!aiConfigured" class="inline-note">No AI service configured. Add your compatible endpoint in Settings.</p>
      </div>
    </section>
    <footer class="page-footer"><span>SCAN {{ String(scan.id).padStart(4, '0') }}</span><span>Missing evidence does not prove technology removal.</span><a :href="reportUrl(scan.id, 'json')" target="_blank" rel="noreferrer">Download JSON ↗</a></footer>
  </div>
</template>
