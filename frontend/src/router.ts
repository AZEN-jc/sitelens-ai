import { createRouter, createWebHistory } from 'vue-router'
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/DashboardView.vue') },
    { path: '/scans/:id', component: () => import('./views/ScanView.vue'), props: true },
    { path: '/compare', component: () => import('./views/CompareView.vue') },
    { path: '/reports', component: () => import('./views/ReportsView.vue') },
    { path: '/settings', component: () => import('./views/SettingsView.vue') },
  ],
})
