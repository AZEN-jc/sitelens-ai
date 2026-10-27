<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import type { Scan } from '../types'

const scans = ref<Scan[]>([])
const before = ref<number | undefined>()
const after = ref<number | undefined>()
const result = ref<Record<string, unknown> | null>(null)
const loading = ref(false)

onMounted(async () => {
  try { scans.value = await api.scans() } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Could not load history.') }
})

async function compare() {
  if (!before.value || !after.value) return
  loading.value = true
  try { result.value = await api.compare(before.value, after.value) }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Comparison failed.') }
  finally { loading.value = false }
}

const groups = [
  { key: 'newly_observed', title: 'Newly observed', caption: 'Evidence present in the newer scan', tone: 'positive' },
  { key: 'not_observed_now', title: 'Not observed now', caption: 'Absence in this response does not prove removal', tone: 'muted' },
  { key: 'evidence_changed', title: 'Evidence changed', caption: 'Technology was seen in both scans with different evidence', tone: 'warning' },
  { key: 'unchanged', title: 'Same evidence', caption: 'Observed in both scans', tone: 'neutral' },
]
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
</script>

<template>
  <div class="page-wrap">
    <div class="page-heading simple-heading"><div><div class="eyebrow">HISTORY / SIDE BY SIDE</div><h1>Compare observations.</h1><p class="subheading">See what changed between two saved scans without overstating what absence means.</p></div></div>
    <section class="compare-picker">
      <label><span class="field-label">EARLIER SCAN</span><el-select v-model="before" placeholder="Select an analysis"><el-option v-for="scan in scans" :key="scan.id" :label="`${new Date(scan.created_at).toLocaleString()} · ${scan.title || hostOf(scan.final_url)}`" :value="scan.id" /></el-select></label>
      <span class="compare-arrow">→</span>
      <label><span class="field-label">LATER SCAN</span><el-select v-model="after" placeholder="Select an analysis"><el-option v-for="scan in scans" :key="scan.id" :label="`${new Date(scan.created_at).toLocaleString()} · ${scan.title || hostOf(scan.final_url)}`" :value="scan.id" /></el-select></label>
      <el-button type="primary" :loading="loading" :disabled="!before || !after || before === after" @click="compare">Compare</el-button>
    </section>
    <div v-if="result" class="comparison-grid">
      <article v-for="group in groups" :key="group.key" class="comparison-card" :class="group.tone"><div class="eyebrow">{{ group.title.toUpperCase() }}</div><p>{{ group.caption }}</p><div v-if="(result[group.key] as string[]).length" class="comparison-items"><span v-for="item in result[group.key] as string[]" :key="item">{{ item }}</span></div><div v-else class="no-diff">No differences</div></article>
    </div>
    <div v-else-if="!scans.length" class="empty-state">Save at least two scans to compare their evidence.</div>
  </div>
</template>
