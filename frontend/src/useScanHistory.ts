import { computed, ref } from 'vue'
import { api } from './api'
import type { Scan } from './types'

const PAGE_SIZE = 30

export function useScanHistory() {
  const scans = ref<Scan[]>([])
  const total = ref(0)
  const loading = ref(true)
  const loadingMore = ref(false)
  const hasMore = computed(() => scans.value.length < total.value)

  async function load() {
    loading.value = true
    try {
      const [items, result] = await Promise.all([api.scans(PAGE_SIZE, 0), api.scanCount()])
      scans.value = items
      total.value = result.count
    } finally {
      loading.value = false
    }
  }

  async function loadMore() {
    if (loadingMore.value || !hasMore.value) return
    loadingMore.value = true
    try {
      scans.value.push(...await api.scans(PAGE_SIZE, scans.value.length))
    } finally {
      loadingMore.value = false
    }
  }

  return { scans, total, loading, loadingMore, hasMore, load, loadMore }
}
