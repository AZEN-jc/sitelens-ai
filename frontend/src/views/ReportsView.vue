<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { RouterLink } from 'vue-router'
import { api, reportUrl } from '../api'
import type { Scan } from '../types'

const scans = ref<Scan[]>([])
const loading = ref(true)
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
onMounted(async () => {
  try { scans.value = await api.scans() } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Could not load reports.') }
  finally { loading.value = false }
})
</script>

<template>
  <div class="page-wrap">
    <div class="page-heading simple-heading"><div><div class="eyebrow">LOCAL ARCHIVE / EXPORTS</div><h1>Reports, kept close.</h1><p class="subheading">Export scan evidence as HTML or JSON. Use your browser’s print dialog to save a PDF.</p></div></div>
    <div v-if="loading" class="empty-state">Loading reports…</div>
    <div v-else-if="!scans.length" class="empty-state report-empty"><span class="empty-symbol">▤</span><b>No saved analyses yet</b><span>Run an authorized scan; each saved result can be exported as HTML or JSON.</span></div>
    <div v-else class="report-list">
      <article v-for="scan in scans" :key="scan.id" class="report-row">
        <div class="report-icon">▤</div><div class="report-copy"><div class="eyebrow">SCAN REPORT · {{ scan.technologies.length }} TECHNOLOGIES · {{ scan.ai_report_count }} AI NOTES</div><RouterLink :to="`/scans/${scan.id}`">{{ scan.title || hostOf(scan.final_url) }}</RouterLink><p>{{ scan.final_url }} · HTTP {{ scan.status_code }}</p></div>
        <time>{{ new Date(scan.created_at).toLocaleString() }}</time><span class="export-links"><a :href="reportUrl(scan.id, 'html')" target="_blank" rel="noreferrer">HTML ↗</a><a :href="reportUrl(scan.id, 'json')" target="_blank" rel="noreferrer">JSON ↗</a></span>
      </article>
    </div>
  </div>
</template>
