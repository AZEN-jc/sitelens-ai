<script setup lang="ts">
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { RouterLink } from 'vue-router'
import { reportUrl } from '../api'
import { useScanHistory } from '../useScanHistory'

const { scans, total, loading, loadingMore, hasMore, load, loadMore } = useScanHistory()
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
onMounted(() => load().catch(error => ElMessage.error(error instanceof Error ? error.message : '无法读取报告。')))
async function showMore() {
  try { await loadMore() } catch (error) { ElMessage.error(error instanceof Error ? error.message : '无法读取更多报告。') }
}
</script>

<template>
  <div class="page-wrap">
    <div class="page-heading simple-heading"><div><div class="eyebrow">本机归档 / 报告导出</div><h1>检测报告</h1><p class="subheading">可将检测证据导出为 HTML 或 JSON，也可使用浏览器的打印功能保存为 PDF。</p></div></div>
    <div v-if="loading" class="empty-state">正在读取报告…</div>
    <div v-else-if="!scans.length" class="empty-state report-empty"><span class="empty-symbol">▤</span><b>暂无已保存的检测</b><span>完成授权检测后，可在此导出对应结果的 HTML 或 JSON 报告。</span></div>
    <div v-else class="report-list">
      <article v-for="scan in scans" :key="scan.id" class="report-row">
        <div class="report-icon">▤</div><div class="report-copy"><div class="eyebrow">检测报告 · {{ scan.technologies.length }} 项技术 · {{ scan.ai_report_count }} 份 AI 分析</div><RouterLink :to="`/scans/${scan.id}`">{{ scan.title || hostOf(scan.final_url) }}</RouterLink><p>{{ scan.final_url }} · HTTP {{ scan.status_code }}</p></div>
        <time>{{ new Date(scan.created_at).toLocaleString('zh-CN') }}</time><span class="export-links"><a :href="reportUrl(scan.id, 'html')" target="_blank" rel="noreferrer">导出 HTML ↗</a><a :href="reportUrl(scan.id, 'json')" target="_blank" rel="noreferrer">导出 JSON ↗</a></span>
      </article>
    </div>
    <div class="history-pagination" v-if="hasMore"><el-button class="history-load-more" :loading="loadingMore" @click="showMore">加载更多检测记录（{{ scans.length }} / {{ total }}）</el-button></div>
  </div>
</template>
