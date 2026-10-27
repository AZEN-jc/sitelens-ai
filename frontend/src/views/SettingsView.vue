<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'

const form = reactive({ base_url: '', api_key: '', model: '' })
const status = ref<{ configured: boolean; base_url?: string; model?: string }>({ configured: false })
const busy = ref(false)
const connection = ref('')

async function refresh() { status.value = await api.aiStatus() }
onMounted(() => refresh().catch(error => ElMessage.error(error.message)))

async function save() {
  busy.value = true
  try {
    await api.configureAI(form.base_url.trim(), form.api_key, form.model.trim())
    form.api_key = ''
    await refresh()
    ElMessage.success('AI 配置已保存到当前服务会话。')
  } catch (error) { ElMessage.error(error instanceof Error ? error.message : '无法保存配置。') }
  finally { busy.value = false }
}

async function test() {
  busy.value = true
  connection.value = ''
  try {
    const result = await api.testAI()
    connection.value = result.ok ? '连接成功，服务返回了有效的对话结果。' : (result.error || '连接测试失败。')
  } catch (error) { connection.value = error instanceof Error ? error.message : '连接测试失败。' }
  finally { busy.value = false }
}

async function clear() {
  busy.value = true
  try { await api.clearAI(); await refresh(); form.api_key = ''; connection.value = ''; ElMessage.success('AI 配置已清除。') }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : '无法清除配置。') }
  finally { busy.value = false }
}
</script>

<template>
  <div class="page-wrap settings-page">
    <div class="page-heading simple-heading"><div><div class="eyebrow">偏好设置 / 模型连接</div><h1>设置</h1><p class="subheading">连接兼容 OpenAI 接口的 AI 服务，用于解释已有检测证据。</p></div></div>
    <section class="settings-card">
      <div class="settings-card-heading"><div><div class="eyebrow">AI 服务</div><h2>配置你使用的模型接口</h2></div><span class="config-status" :class="{ ready: status.configured }"><i></i>{{ status.configured ? '已配置' : '未连接' }}</span></div>
      <div class="active-config" v-if="status.configured"><span>当前接口</span><b>{{ status.base_url }}</b><span>模型 · {{ status.model }}</span></div>
      <form class="settings-form" @submit.prevent="save">
        <label><span class="field-label">接口地址</span><el-input v-model="form.base_url" placeholder="https://api.example.com/v1" autocomplete="url" required maxlength="2048" /></label>
        <label><span class="field-label">模型名称</span><el-input v-model="form.model" placeholder="model-name" required maxlength="200" /></label>
        <label class="wide-field"><span class="field-label">API 密钥</span><el-input v-model="form.api_key" type="password" show-password autocomplete="new-password" placeholder="输入本次服务会话使用的密钥（至少 8 个字符）" required minlength="8" maxlength="4096" /></label>
        <div class="settings-actions"><el-button type="primary" native-type="submit" :loading="busy">保存配置</el-button><el-button :disabled="!status.configured || busy" @click="test">测试连接</el-button><el-button v-if="status.configured" :disabled="busy" @click="clear">清除配置</el-button></div>
      </form>
      <p v-if="connection" class="connection-result" role="status">{{ connection }}</p>
      <div class="security-note"><span>◈</span><p><b>密钥仅保存在当前会话。</b> 密钥只留在后端内存中，服务重启后失效；不会返回到页面，也不会写入历史记录。配置本机或私有网络接口，即表示允许服务连接该地址。</p></div>
    </section>
    <section class="settings-card local-card"><div class="eyebrow">本机存储</div><h2>检测历史记录</h2><p>检测摘要和证据保存在本机 SQLite 数据库中。分析完成后会丢弃完整网页内容。生成的 AI 分析会与对应检测记录一起保存。</p></section>
  </div>
</template>
