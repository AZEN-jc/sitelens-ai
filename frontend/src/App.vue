<script setup lang="ts">
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}
const links = [
  { label: '概览', to: '/', icon: '◫' },
  { label: '历史对比', to: '/compare', icon: '⇄' },
  { label: '报告', to: '/reports', icon: '▤' },
  { label: '设置', to: '/settings', icon: '⚙' },
]
</script>

<template>
  <div class="app-frame">
    <aside class="sidebar">
      <button type="button" class="back-btn" @click="goBack">
        <span class="back-arrow">←</span>
        <span class="back-text"><b>返回</b><small>回到上一个页面</small></span>
      </button>
      <div class="nav-group-label">工作区</div>
      <nav class="side-nav" aria-label="主导航">
        <RouterLink v-for="item in links" :key="item.to" :to="item.to" :class="{ active: route.path === item.to || (item.to === '/' && route.path.startsWith('/scans/')) }">
          <span class="nav-icon">{{ item.icon }}</span>{{ item.label }}
        </RouterLink>
      </nav>
      <div class="sidebar-bottom">
        <div class="local-status"><i></i><span><b>本机运行</b><small>数据保存在此设备</small></span></div>
      </div>
    </aside>
    <main class="main-pane">
      <header class="topbar">
        <div class="breadcrumb">SiteLens <span>/</span> <b>{{ route.path.startsWith('/scans/') ? '检测结果' : links.find(item => item.to === route.path)?.label || '概览' }}</b></div>
        <div class="topbar-right"><span class="private-pill"><i></i>仅本机</span></div>
      </header>
      <RouterView />
    </main>
  </div>
</template>
