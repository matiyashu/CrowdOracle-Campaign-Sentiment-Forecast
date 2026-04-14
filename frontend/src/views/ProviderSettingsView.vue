<template>
  <div class="providers-container">
    <nav class="navbar">
      <div class="nav-brand">CROWDORACLE</div>
      <div class="nav-links">
        <router-link to="/campaigns" class="nav-link">← Campaigns</router-link>
      </div>
    </nav>

    <div class="page-content">
      <div class="page-header">
        <div>
          <span class="orange-tag">LLM CONFIGURATION</span>
          <h1 class="page-title">Provider Settings</h1>
          <p class="page-desc">Configure AI providers and route each analysis task to the right model.</p>
        </div>
        <button class="btn-primary" @click="showAdd = true">+ Add Provider</button>
      </div>

      <div class="providers-layout">
        <!-- Provider list -->
        <div class="provider-list">
          <div
            v-for="p in providers"
            :key="p.id"
            class="provider-item"
            :class="{ active: p.is_active, selected: selected?.id === p.id }"
            @click="selected = p"
          >
            <div class="provider-type-badge">{{ p.provider_type }}</div>
            <div class="provider-name">{{ p.name }}</div>
            <div class="provider-model">{{ p.default_model }}</div>
            <div v-if="p.is_active" class="provider-active-tag">ACTIVE</div>
          </div>

          <div v-if="providers.length === 0" class="empty-list">No providers yet.</div>
        </div>

        <!-- Detail / edit panel -->
        <div class="provider-detail" v-if="selected">
          <div class="detail-header">
            <span class="detail-type">{{ selected.provider_type.toUpperCase() }}</span>
            <div class="detail-actions">
              <button v-if="!selected.is_active" class="btn-ghost" @click="setActive(selected.id)">Set Active</button>
              <button class="btn-danger" @click="deleteProvider(selected.id)">Delete</button>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">Connection</h3>
            <div class="form-grid">
              <label class="form-label">Name
                <input v-model="editForm.name" class="form-input" />
              </label>
              <label class="form-label">Provider Type
                <select v-model="editForm.provider_type" class="form-input">
                  <option v-for="t in providerTypes" :key="t" :value="t">{{ t }}</option>
                </select>
              </label>
              <label class="form-label full-width">API Key
                <input v-model="editForm.api_key" type="password" class="form-input" placeholder="sk-…" />
              </label>
              <label class="form-label full-width">Base URL
                <input v-model="editForm.base_url" class="form-input" :placeholder="placeholderUrl" />
              </label>
              <label class="form-label">Default Model
                <input v-model="editForm.default_model" class="form-input" placeholder="e.g. gpt-4o" />
              </label>
              <label class="form-label">Fallback Model
                <input v-model="editForm.fallback_model" class="form-input" placeholder="e.g. gpt-4o-mini" />
              </label>
              <label class="form-label">Max Tokens
                <input v-model.number="editForm.max_tokens" type="number" class="form-input" />
              </label>
              <label class="form-label">Temperature
                <input v-model.number="editForm.temperature" type="number" step="0.1" min="0" max="2" class="form-input" />
              </label>
              <label class="form-label check-label">
                <input type="checkbox" v-model="editForm.multimodal_enabled" />
                Multimodal enabled (vision/image analysis)
              </label>
            </div>

            <div class="test-row">
              <button class="btn-ghost" @click="testConnection" :disabled="testing">
                {{ testing ? 'Testing…' : 'Test Connection' }}
              </button>
              <span class="test-result" :class="testResult?.ok ? 'ok' : 'fail'" v-if="testResult">
                {{ testResult.ok ? '✓' : '✗' }} {{ testResult.message }}
              </span>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">Task Routing</h3>
            <p class="section-hint">Override the default model for specific analysis tasks.</p>
            <div class="routing-grid">
              <label v-for="task in taskNames" :key="task" class="form-label">
                {{ task }}
                <input v-model="editForm.task_routing[task]" class="form-input" :placeholder="editForm.default_model || 'default'" />
              </label>
            </div>
          </div>

          <div class="form-footer">
            <span v-if="saveMsg" class="save-msg">{{ saveMsg }}</span>
            <button class="btn-primary" @click="saveProvider">Save Changes</button>
          </div>
        </div>

        <div v-else class="provider-detail empty-detail">
          <p>Select a provider from the list, or add a new one.</p>
        </div>
      </div>
    </div>

    <!-- Add provider modal -->
    <div v-if="showAdd" class="modal-overlay" @click.self="showAdd = false">
      <div class="modal">
        <div class="modal-header">
          <span>Add Provider</span>
          <button class="modal-close" @click="showAdd = false">✕</button>
        </div>
        <div class="form-grid pad">
          <label class="form-label">Name *
            <input v-model="newForm.name" class="form-input" placeholder="My OpenAI" />
          </label>
          <label class="form-label">Provider Type *
            <select v-model="newForm.provider_type" class="form-input">
              <option v-for="t in providerTypes" :key="t" :value="t">{{ t }}</option>
            </select>
          </label>
          <label class="form-label full-width">API Key
            <input v-model="newForm.api_key" type="password" class="form-input" />
          </label>
          <label class="form-label full-width">Base URL
            <input v-model="newForm.base_url" class="form-input" placeholder="Leave blank for defaults" />
          </label>
          <label class="form-label">Default Model
            <input v-model="newForm.default_model" class="form-input" placeholder="gpt-4o-mini" />
          </label>
        </div>
        <div v-if="addError" class="form-error">{{ addError }}</div>
        <div class="modal-footer">
          <button class="btn-ghost" @click="showAdd = false">Cancel</button>
          <button class="btn-primary" :disabled="adding" @click="addProvider">
            {{ adding ? 'Adding…' : 'Add Provider' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { providersApi } from '../api/providers'

const providers = ref([])
const selected = ref(null)
const showAdd = ref(false)
const adding = ref(false)
const addError = ref('')
const testing = ref(false)
const testResult = ref(null)
const saveMsg = ref('')

const providerTypes = ['openai', 'anthropic', 'qwen', 'gemini', 'custom']
const taskNames = ['creative_vision', 'sentiment', 'report_writer', 'simulation', 'transcript', 'chat', 'keyword', 'impact']

const newForm = ref({ name: '', provider_type: 'openai', api_key: '', base_url: '', default_model: '' })
const editForm = ref({ name: '', provider_type: 'openai', api_key: '', base_url: '', default_model: '',
  fallback_model: '', max_tokens: 4096, temperature: 0.3, multimodal_enabled: false, task_routing: {} })

const placeholderUrl = computed(() => {
  const map = {
    openai: 'https://api.openai.com/v1',
    anthropic: '(uses Anthropic SDK directly)',
    qwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    gemini: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    custom: 'https://your-endpoint/v1',
  }
  return map[editForm.value.provider_type] || ''
})

watch(selected, (p) => {
  if (!p) return
  editForm.value = {
    name: p.name,
    provider_type: p.provider_type,
    api_key: '',
    base_url: p.base_url || '',
    default_model: p.default_model || '',
    fallback_model: p.fallback_model || '',
    max_tokens: p.max_tokens || 4096,
    temperature: p.temperature ?? 0.3,
    multimodal_enabled: p.multimodal_enabled || false,
    task_routing: { ...( p.task_routing || {}) },
  }
  testResult.value = null
  saveMsg.value = ''
})

async function loadProviders() {
  try {
    const res = await providersApi.list()
    providers.value = res.data.data || []
  } catch {
    providers.value = []
  }
}

async function addProvider() {
  addError.value = ''
  if (!newForm.value.name) { addError.value = 'Name is required.'; return }
  adding.value = true
  try {
    await providersApi.save(newForm.value)
    showAdd.value = false
    await loadProviders()
  } catch (err) {
    addError.value = err.response?.data?.error || 'Failed to add provider.'
  } finally {
    adding.value = false
  }
}

async function saveProvider() {
  saveMsg.value = ''
  try {
    await providersApi.patch(selected.value.id, editForm.value)
    if (Object.keys(editForm.value.task_routing || {}).length) {
      await providersApi.saveTaskRouting(editForm.value.task_routing)
    }
    saveMsg.value = '✓ Saved.'
    await loadProviders()
  } catch (err) {
    saveMsg.value = `✗ ${err.response?.data?.error || err.message}`
  }
}

async function setActive(id) {
  await providersApi.setActive(id)
  await loadProviders()
  selected.value = providers.value.find(p => p.id === id) || null
}

async function deleteProvider(id) {
  if (!confirm('Delete this provider?')) return
  await providersApi.remove(id)
  selected.value = null
  await loadProviders()
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    const res = await providersApi.testConnection({
      provider_type: editForm.value.provider_type,
      api_key: editForm.value.api_key,
      base_url: editForm.value.base_url,
      default_model: editForm.value.default_model,
    })
    testResult.value = res.data.data
  } catch {
    testResult.value = { ok: false, message: 'Request failed.' }
  } finally {
    testing.value = false
  }
}

onMounted(loadProviders)
</script>

<style scoped>
.providers-container { min-height: 100vh; background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 32px; border-bottom: 1px solid #222; }
.nav-brand { font-size: 14px; font-weight: 700; letter-spacing: 4px; }
.nav-links { display: flex; gap: 24px; }
.nav-link { color: #888; text-decoration: none; font-size: 12px; }
.nav-link:hover { color: #fff; }

.page-content { padding: 40px 32px; max-width: 1280px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
.orange-tag { background: #f60; color: #000; font-size: 10px; font-weight: 700; letter-spacing: 2px; padding: 3px 8px; }
.page-title { font-size: 36px; font-weight: 700; margin: 12px 0 8px; }
.page-desc { color: #666; font-size: 13px; }

.providers-layout { display: grid; grid-template-columns: 240px 1fr; gap: 24px; }

.provider-list { display: flex; flex-direction: column; gap: 1px; }
.provider-item { border: 1px solid #1a1a1a; padding: 14px 16px; cursor: pointer; transition: border-color 0.2s; position: relative; }
.provider-item:hover { border-color: #333; }
.provider-item.selected { border-color: #f60; }
.provider-item.active { border-left: 3px solid #0f0; }
.provider-type-badge { font-size: 10px; color: #555; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; }
.provider-name { font-size: 13px; font-weight: 700; }
.provider-model { font-size: 11px; color: #888; margin-top: 2px; }
.provider-active-tag { position: absolute; top: 8px; right: 8px; font-size: 9px; color: #0f0; letter-spacing: 2px; }
.empty-list { color: #444; font-size: 12px; padding: 16px; }

.provider-detail { border: 1px solid #222; padding: 28px; }
.empty-detail { display: flex; align-items: center; justify-content: center; color: #444; font-size: 13px; }

.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.detail-type { font-size: 11px; letter-spacing: 3px; color: #f60; }
.detail-actions { display: flex; gap: 10px; }

.form-section { margin-bottom: 32px; }
.section-title { font-size: 12px; letter-spacing: 2px; color: #888; margin-bottom: 16px; text-transform: uppercase; }
.section-hint { font-size: 12px; color: #555; margin-bottom: 12px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-grid.pad { padding: 24px; }
.form-label { display: flex; flex-direction: column; gap: 5px; font-size: 11px; color: #888; letter-spacing: 1px; }
.form-label.full-width { grid-column: span 2; }
.form-label.check-label { flex-direction: row; align-items: center; gap: 10px; font-size: 12px; color: #aaa; }
.form-input { background: #111; border: 1px solid #333; color: #fff; padding: 8px 12px; font-family: inherit; font-size: 12px; }
.form-input:focus { outline: none; border-color: #f60; }
select.form-input { cursor: pointer; }

.routing-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }

.test-row { display: flex; align-items: center; gap: 16px; margin-top: 16px; }
.test-result { font-size: 12px; }
.test-result.ok { color: #0f0; }
.test-result.fail { color: #f44; }

.form-footer { display: flex; align-items: center; justify-content: flex-end; gap: 16px; padding-top: 20px; border-top: 1px solid #1a1a1a; }
.save-msg { font-size: 12px; color: #0f0; }

.btn-primary { background: #f60; color: #000; border: none; padding: 10px 20px; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
.btn-primary:hover { background: #e55a00; }
.btn-primary:disabled { opacity: 0.5; cursor: default; }
.btn-ghost { background: transparent; color: #fff; border: 1px solid #333; padding: 10px 20px; font-family: inherit; font-size: 12px; cursor: pointer; }
.btn-ghost:hover { border-color: #fff; }
.btn-ghost:disabled { opacity: 0.5; cursor: default; }
.btn-danger { background: transparent; color: #f44; border: 1px solid #f44; padding: 10px 20px; font-family: inherit; font-size: 12px; cursor: pointer; }
.btn-danger:hover { background: #f44; color: #000; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #0a0a0a; border: 1px solid #333; width: 480px; max-width: 95vw; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #222; font-size: 14px; font-weight: 700; letter-spacing: 2px; }
.modal-close { background: none; border: none; color: #888; font-size: 18px; cursor: pointer; }
.modal-close:hover { color: #fff; }
.form-error { margin: 0 24px; color: #f44; font-size: 12px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 20px 24px; border-top: 1px solid #222; }
</style>
