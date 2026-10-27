<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { router } from '../router'

const url = ref('')
const authorized = ref(false)
const loading = ref(false)

async function submit() {
  if (!authorized.value) return
  loading.value = true
  try {
    const scan = await api.createScan(url.value.trim())
    await router.push(`/scans/${scan.id}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : 'Scan failed.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form class="scan-form" @submit.prevent="submit">
    <label class="field-label" for="target-url">Website URL</label>
    <div class="scan-input-row">
      <span class="input-prefix">↗</span>
      <el-input id="target-url" v-model="url" placeholder="https://your-authorized-site.com" type="url" required maxlength="2048" />
      <el-button type="primary" native-type="submit" :loading="loading" :disabled="!authorized || !url.trim()">
        Analyze <span aria-hidden="true">↗</span>
      </el-button>
    </div>
    <label class="authorization"><input v-model="authorized" type="checkbox" required />
      I own this website or have permission to analyze its public technology signals.
    </label>
  </form>
</template>
