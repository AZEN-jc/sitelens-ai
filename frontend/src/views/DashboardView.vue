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
  try { scans.value = await api.scans() } catch (error) { ElMessage.error(error instanceof Error ? error.message : '无法读取检测记录。') }
  finally { loading.value = false }
})

function date(value: string) { return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) }
function hostOf(value: string) { try { return new URL(value).hostname } catch { return value } }
</script>

<template>
  <div class="page-wrap">
    <div class="page-heading">
      <div><div class="eyebrow">网站技术识别 <span>—</span> 基于公开证据</div><h1>看清网站<br class="mobile-break" />正在使用什么。</h1><p class="subheading">仅分析你拥有或获准检测的网站公开技术特征，并展示对应证据。</p></div>
      <div class="edition-stamp"><span>本机版 · 01</span><b>本地分析<br />数据留在设备</b><i>◈</i></div>
    </div>

    <section class="scan-panel">
      <div class="section-kicker"><span class="step-dot">01</span>输入网址并开始检测<span class="hairline"></span><span class="micro-note">仅采集公开信息</span></div>
      <ScanForm />
    </section>

    <section class="stats-grid" aria-label="检测概览">
      <article class="stat-card"><span class="stat-label">检测记录</span><strong>{{ scans.length.toString().padStart(2, '0') }}</strong><span class="stat-foot">保存在本机历史记录</span></article>
      <article class="stat-card accent-stat"><span class="stat-label">已观察到的技术</span><strong>{{ technologies.toString().padStart(2, '0') }}</strong><span class="stat-foot">统计历史检测中的技术</span></article>
      <article class="stat-card"><span class="stat-label">最近检测</span><strong class="stat-date">{{ latest ? date(latest) : '—' }}</strong><span class="stat-foot">不与云端同步</span></article>
    </section>

    <section class="history-section">
      <div class="section-title-row"><div><div class="eyebrow">本机工作区</div><h2>最近检测</h2></div><RouterLink class="text-link" to="/compare">对比历史记录 <span>↗</span></RouterLink></div>
      <div v-if="loading" class="empty-state">正在读取本机历史记录…</div>
      <div v-else-if="!scans.length" class="empty-state"><span class="empty-symbol">◌</span><b>还没有检测记录</b><span>完成第一次授权检测后，结果会显示在这里。</span></div>
      <div v-else class="history-table">
        <div class="history-head"><span>目标网站</span><span>观察到的技术</span><span>状态</span><span>日期</span><span></span></div>
        <RouterLink v-for="scan in scans.slice(0, 8)" :key="scan.id" :to="`/scans/${scan.id}`" class="history-row">
          <span class="target-cell"><i class="target-icon">↗</i><span><b>{{ scan.title || hostOf(scan.final_url) }}</b><small>{{ hostOf(scan.final_url) }}</small></span></span>
          <span class="tech-chips"><span v-for="tech in scan.technologies.slice(0, 3)" :key="tech.name">{{ tech.name }}</span><small v-if="scan.technologies.length > 3">+{{ scan.technologies.length - 3 }}</small><small v-if="!scan.technologies.length">未匹配到指纹</small></span>
          <span class="status-label"><i></i> 已完成</span>
          <span class="date-cell">{{ date(scan.created_at) }}</span><span class="row-arrow">→</span>
        </RouterLink>
      </div>
    </section>
    <footer class="page-footer"><span>◈ SiteLens AI</span><span>识别结果由公开证据支持；架构关系仅为推测。</span><span>v0.1.0</span></footer>
  </div>
</template>
