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
    ElMessage.error(error instanceof Error ? error.message : '检测失败。')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form class="scan-form" @submit.prevent="submit">
    <label class="field-label" for="target-url">网站地址</label>
    <div class="scan-input-row">
      <span class="input-prefix">↗</span>
      <el-input id="target-url" v-model="url" placeholder="https://your-authorized-site.com" type="url" required maxlength="2048" />
      <el-button type="primary" native-type="submit" :loading="loading" :disabled="!authorized || !url.trim()">
        开始检测 <span aria-hidden="true">↗</span>
      </el-button>
    </div>
    <label class="authorization"><input v-model="authorized" type="checkbox" required />
      我拥有该网站，或已获准检测其公开技术特征。
    </label>
  </form>
</template>
