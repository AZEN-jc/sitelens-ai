<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { router } from '../router'

const url = ref('')
const loading = ref(false)

async function submit() {
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
      <el-input id="target-url" v-model="url" placeholder="example.com 或 https://完整网址" type="text" inputmode="url" required maxlength="2048" />
      <el-button type="primary" native-type="submit" :loading="loading" :disabled="!url.trim()">
        开始检测 <span aria-hidden="true">↗</span>
      </el-button>
    </div>
  </form>
</template>
