<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()
const links = [
  { label: 'Overview', to: '/', icon: '◫' },
  { label: 'Compare', to: '/compare', icon: '⇄' },
  { label: 'Reports', to: '/reports', icon: '▤' },
]
</script>

<template>
  <div class="app-frame">
    <aside class="sidebar">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">◈</span>
        <span><strong>SiteLens</strong><small>TECH INTELLIGENCE</small></span>
      </RouterLink>
      <div class="nav-group-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="Main navigation">
        <RouterLink v-for="item in links" :key="item.to" :to="item.to" :class="{ active: route.path === item.to || (item.to === '/' && route.path.startsWith('/scans/')) }">
          <span class="nav-icon">{{ item.icon }}</span>{{ item.label }}
        </RouterLink>
      </nav>
      <div class="sidebar-bottom">
        <div class="local-status"><i></i><span><b>Local session</b><small>Data stays on this device</small></span></div>
        <RouterLink to="/settings" class="settings-link" :class="{ active: route.path === '/settings' }"><span class="nav-icon">⚙</span>Settings</RouterLink>
      </div>
    </aside>
    <main class="main-pane">
      <header class="topbar">
        <div class="breadcrumb">SiteLens <span>/</span> <b>{{ route.path.startsWith('/scans/') ? 'Analysis' : route.path.slice(1) || 'Overview' }}</b></div>
        <div class="topbar-right"><span class="private-pill"><i></i> LOCAL ONLY</span><RouterLink to="/settings" aria-label="Settings" class="top-avatar">SL</RouterLink></div>
      </header>
      <RouterView />
    </main>
  </div>
</template>
