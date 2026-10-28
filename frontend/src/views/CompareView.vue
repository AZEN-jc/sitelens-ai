<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import type { Scan } from '../types'
import { useScanHistory } from '../useScanHistory'

const { scans, total, loading: historyLoading, loadingMore, hasMore, load, loadMore } = useScanHistory()
const before = ref<number | undefined>()
const after = ref<number | undefined>()
const result = ref<Record<string, unknown> | null>(null)
const comparing = ref(false)

onMounted(() => load().catch(error => ElMessage.error(error instanceof Error ? error.message : '无法读取检测历史。')))

async function showMore() {
  try { await loadMore() } catch (error) { ElMessage.error(error instanceof Error ? error.message : '无法读取更多检测记录。') }
}

async function compare() {
  if (!before.value || !after.value) return
  comparing.value = true
  try { result.value = await api.compare(before.value, after.value) }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : '对比失败。') }
  finally { comparing.value = false }
}

const groups = [
  { key: 'newly_observed', title: '本次新观察到', caption: '较新的检测中出现了相关证据', tone: 'positive' },
  { key: 'not_observed_now', title: '本次未观察到', caption: '本次响应中缺少证据，不代表技术已被移除', tone: 'muted' },
  { key: 'evidence_changed', title: '证据发生变化', caption: '两次检测都观察到该技术，但证据不同', tone: 'warning' },
  { key: 'unchanged', title: '证据相同', caption: '两次检测都观察到了相同证据', tone: 'neutral' },
]
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
</script>

<template>
  <div class="page-wrap">
    <div class="page-heading simple-heading"><div><div class="eyebrow">检测历史 / 并排对比</div><h1>对比检测结果</h1><p class="subheading">查看两次检测的证据变化；未观察到某项技术，不代表它已被移除。</p></div></div>
    <section class="compare-picker">
      <label><span class="field-label">较早的检测</span><el-select v-model="before" placeholder="选择一条检测记录"><el-option v-for="scan in scans" :key="scan.id" :label="`${new Date(scan.created_at).toLocaleString('zh-CN')} · ${scan.title || hostOf(scan.final_url)}`" :value="scan.id" /></el-select></label>
      <span class="compare-arrow">→</span>
      <label><span class="field-label">较新的检测</span><el-select v-model="after" placeholder="选择一条检测记录"><el-option v-for="scan in scans" :key="scan.id" :label="`${new Date(scan.created_at).toLocaleString('zh-CN')} · ${scan.title || hostOf(scan.final_url)}`" :value="scan.id" /></el-select></label>
      <el-button type="primary" :loading="comparing" :disabled="!before || !after || before === after" @click="compare">开始对比</el-button>
    </section>
    <div class="history-pagination" v-if="hasMore"><el-button class="history-load-more" :loading="loadingMore" @click="showMore">加载更多检测记录（{{ scans.length }} / {{ total }}）</el-button></div>
    <div v-if="historyLoading" class="empty-state">正在读取检测历史…</div>
    <div v-else-if="result" class="comparison-grid">
      <article v-for="group in groups" :key="group.key" class="comparison-card" :class="group.tone"><div class="eyebrow">{{ group.title }}</div><p>{{ group.caption }}</p><div v-if="(result[group.key] as string[]).length" class="comparison-items"><span v-for="item in result[group.key] as string[]" :key="item">{{ item }}</span></div><div v-else class="no-diff">没有差异</div></article>
    </div>
    <div v-else-if="!scans.length" class="empty-state">至少保存两次检测，才能对比证据变化。</div>
  </div>
</template>
