<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { RouterLink } from 'vue-router'
import { api } from '../api'
import ScanForm from '../components/ScanForm.vue'
import type { Scan } from '../types'

const scans = ref<Scan[]>([])
const loading = ref(true)
const technologies = computed(() => new Set(scans.value.flatMap(scan => scan.technologies.map(item => item.name))).size)
const latest = computed(() => scans.value[0]?.created_at)

onMounted(async () => {
  try { scans.value = await api.scans() } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Could not load scans.') }
  finally { loading.value = false }
})

function date(value: string) { return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) }
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
</script>

<template>
  <div class="page-wrap">
    <div class="page-heading">
      <div><div class="eyebrow">FIELD NOTES <span>—</span> WEB TECHNOLOGY</div><h1>Understand what<br class="mobile-break" /> runs the web.</h1><p class="subheading">Evidence-led technology analysis for sites you’re authorized to inspect.</p></div>
      <div class="edition-stamp"><span>EDITION 01</span><b>LOCAL<br />INTELLIGENCE</b><i>◈</i></div>
    </div>

    <section class="scan-panel">
      <div class="section-kicker"><span class="step-dot">01</span> START AN ANALYSIS <span class="hairline"></span><span class="micro-note">PUBLIC SIGNALS ONLY</span></div>
      <ScanForm />
    </section>

    <section class="stats-grid" aria-label="Workspace summary">
      <article class="stat-card"><span class="stat-label">TOTAL ANALYSES</span><strong>{{ scans.length.toString().padStart(2, '0') }}</strong><span class="stat-foot">Saved in local history</span></article>
      <article class="stat-card accent-stat"><span class="stat-label">TECHNOLOGIES OBSERVED</span><strong>{{ technologies.toString().padStart(2, '0') }}</strong><span class="stat-foot">Across recent scans</span></article>
      <article class="stat-card"><span class="stat-label">LAST ANALYSIS</span><strong class="stat-date">{{ latest ? date(latest) : '—' }}</strong><span class="stat-foot">No cloud sync</span></article>
    </section>

    <section class="history-section">
      <div class="section-title-row"><div><div class="eyebrow">YOUR WORKSPACE</div><h2>Recent analyses</h2></div><RouterLink class="text-link" to="/compare">Compare history <span>↗</span></RouterLink></div>
      <div v-if="loading" class="empty-state">Loading local history…</div>
      <div v-else-if="!scans.length" class="empty-state"><span class="empty-symbol">◌</span><b>No analyses yet</b><span>Your first authorized scan will appear here.</span></div>
      <div v-else class="history-table">
        <div class="history-head"><span>TARGET</span><span>OBSERVED STACK</span><span>STATUS</span><span>DATE</span><span></span></div>
        <RouterLink v-for="scan in scans.slice(0, 8)" :key="scan.id" :to="`/scans/${scan.id}`" class="history-row">
          <span class="target-cell"><i class="target-icon">↗</i><span><b>{{ scan.title || hostOf(scan.final_url) }}</b><small>{{ hostOf(scan.final_url) }}</small></span></span>
          <span class="tech-chips"><span v-for="tech in scan.technologies.slice(0, 3)" :key="tech.name">{{ tech.name }}</span><small v-if="scan.technologies.length > 3">+{{ scan.technologies.length - 3 }}</small><small v-if="!scan.technologies.length">No fingerprints</small></span>
          <span class="status-label"><i></i> COMPLETE</span>
          <span class="date-cell">{{ date(scan.created_at) }}</span><span class="row-arrow">→</span>
        </RouterLink>
      </div>
    </section>
    <footer class="page-footer"><span>◈ Sitelens AI</span><span>Observed signals are evidence. Architecture is an informed hypothesis.</span><span>v0.1.0</span></footer>
  </div>
</template>
