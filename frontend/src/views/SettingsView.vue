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
    ElMessage.success('Configuration saved for this backend session.')
  } catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Could not save configuration.') }
  finally { busy.value = false }
}

async function test() {
  busy.value = true
  connection.value = ''
  try {
    const result = await api.testAI()
    connection.value = result.ok ? 'Connected. The endpoint returned a valid chat response.' : (result.error || 'Connection test failed.')
  } catch (error) { connection.value = error instanceof Error ? error.message : 'Connection test failed.' }
  finally { busy.value = false }
}

async function clear() {
  busy.value = true
  try { await api.clearAI(); await refresh(); form.api_key = ''; connection.value = ''; ElMessage.success('AI configuration cleared.') }
  catch (error) { ElMessage.error(error instanceof Error ? error.message : 'Could not clear configuration.') }
  finally { busy.value = false }
}
</script>

<template>
  <div class="page-wrap settings-page">
    <div class="page-heading simple-heading"><div><div class="eyebrow">PREFERENCES / MODEL CONNECTION</div><h1>Settings.</h1><p class="subheading">Connect an OpenAI-compatible service for evidence-based explanations.</p></div></div>
    <section class="settings-card">
      <div class="settings-card-heading"><div><div class="eyebrow">AI SERVICE</div><h2>Bring your own endpoint</h2></div><span class="config-status" :class="{ ready: status.configured }"><i></i>{{ status.configured ? 'CONFIGURED' : 'NOT CONNECTED' }}</span></div>
      <div class="active-config" v-if="status.configured"><span>Current endpoint</span><b>{{ status.base_url }}</b><span>Model · {{ status.model }}</span></div>
      <form class="settings-form" @submit.prevent="save">
        <label><span class="field-label">API BASE URL</span><el-input v-model="form.base_url" placeholder="https://api.example.com/v1" autocomplete="url" required maxlength="2048" /></label>
        <label><span class="field-label">MODEL NAME</span><el-input v-model="form.model" placeholder="model-name" required maxlength="200" /></label>
        <label class="wide-field"><span class="field-label">API KEY</span><el-input v-model="form.api_key" type="password" show-password autocomplete="new-password" placeholder="Enter a key for this session (8+ characters)" required minlength="8" maxlength="4096" /></label>
        <div class="settings-actions"><el-button type="primary" native-type="submit" :loading="busy">Save in this session</el-button><el-button :disabled="!status.configured || busy" @click="test">Test connection</el-button><el-button v-if="status.configured" :disabled="busy" @click="clear">Clear</el-button></div>
      </form>
      <p v-if="connection" class="connection-result" role="status">{{ connection }}</p>
      <div class="security-note"><span>◈</span><p><b>Session-only secret.</b> The key stays in backend memory until the service restarts. It is not returned to this page or written to history. If you configure a private or local endpoint, you are explicitly allowing this service to connect to it.</p></div>
    </section>
    <section class="settings-card local-card"><div class="eyebrow">LOCAL STORAGE</div><h2>Your analysis history</h2><p>Scan summaries and evidence are stored in the local SQLite database. Full page HTML is discarded after analysis. AI reports you generate are saved with their scan.</p></section>
  </div>
</template>
