<template>
  <section class="prov">
    <header class="prov__head">
      <div>
        <span class="prov__eyebrow">LLM PROVIDERS</span>
        <h1>Route every task to the model you trust.</h1>
        <p>Connect OpenAI, Anthropic, Qwen, Gemini, or any OpenAI-compatible endpoint.</p>
      </div>
      <button class="btn btn--primary" @click="startNew">+ Add provider</button>
    </header>

    <div v-if="store.loading && !store.list.length" class="skeletons">
      <LoadingSkeleton v-for="i in 3" :key="i" height="80px" />
    </div>

    <ErrorState
      v-else-if="store.error"
      title="Couldn't load providers."
      :body="String(store.error?.message || store.error)"
      @retry="store.loadList()"
    />

    <EmptyState
      v-else-if="!store.list.length && !drafting"
      title="No AI providers configured."
      body="Connect at least one provider so CrowdOracle can analyze creatives and run reports."
    >
      <button class="btn btn--primary" @click="startNew">+ Add provider</button>
    </EmptyState>

    <div v-else class="layout">
      <aside class="layout__list">
        <article
          v-for="p in store.list"
          :key="p.id"
          class="card"
          :class="{ 'card--on': isSelected(p), 'card--active': p.is_active }"
          @click="selectExisting(p)"
        >
          <header class="card__head">
            <span class="card__name">{{ p.name }}</span>
            <span v-if="p.is_active" class="card__active">ACTIVE</span>
          </header>
          <div class="card__meta">
            <span>{{ p.provider_type }}</span>
            <span class="card__sep">·</span>
            <span>{{ p.default_model || '—' }}</span>
          </div>
        </article>

        <article
          v-if="drafting"
          class="card card--on card--draft"
          @click.stop
        >
          <header class="card__head">
            <span class="card__name">New provider</span>
            <span class="card__active">DRAFT</span>
          </header>
          <div class="card__meta">
            <span>{{ form.provider_type }}</span>
          </div>
        </article>
      </aside>

      <section v-if="form" class="form">
        <div class="form__grid">
          <label class="field">
            <span>Name</span>
            <input v-model="form.name" placeholder="e.g. Anthropic — production" />
          </label>
          <label class="field">
            <span>Provider type</span>
            <select v-model="form.provider_type" @change="applyDefaults">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="qwen">Qwen</option>
              <option value="gemini">Gemini</option>
              <option value="custom">Custom (OpenAI-compatible)</option>
            </select>
          </label>
          <label class="field field--wide">
            <span>Base URL</span>
            <input v-model="form.base_url" :placeholder="defaultBaseUrl" />
          </label>
          <label class="field field--wide">
            <span>API key</span>
            <input v-model="form.api_key" type="password" autocomplete="new-password" placeholder="sk-…" />
          </label>
          <label class="field">
            <span>Default model</span>
            <input v-model="form.default_model" :placeholder="defaultModel" />
          </label>
          <label class="field">
            <span>Fallback model</span>
            <input v-model="form.fallback_model" placeholder="optional" />
          </label>
          <label class="field">
            <span>Temperature</span>
            <input v-model.number="form.temperature" type="number" step="0.1" min="0" max="2" />
          </label>
          <label class="field">
            <span>Max tokens</span>
            <input v-model.number="form.max_tokens" type="number" step="256" min="256" />
          </label>
          <label class="field field--wide check">
            <input v-model="form.multimodal_enabled" type="checkbox" />
            <span>Multimodal enabled (image + video understanding)</span>
          </label>
        </div>

        <div v-if="store.lastTest" class="test" :class="store.lastTest.ok ? 'test--ok' : 'test--err'">
          <strong>{{ store.lastTest.ok ? 'Connected.' : 'Connection failed.' }}</strong>
          <span>{{ store.lastTest.detail }}</span>
          <span v-if="store.lastTest.latency_ms">· {{ store.lastTest.latency_ms }}ms</span>
        </div>

        <div v-if="saveMsg" class="test" :class="'test--' + saveMsg.state">
          {{ saveMsg.text }}
        </div>

        <footer class="form__foot">
          <button class="btn btn--ghost" :disabled="busy" @click="testConnection">Test connection</button>
          <span class="form__spacer"></span>
          <button
            v-if="selected && !selected.is_active"
            class="btn btn--ghost"
            :disabled="busy"
            @click="activate"
          >Set active</button>
          <button
            v-if="selected"
            class="btn btn--danger"
            :disabled="busy"
            @click="remove"
          >Delete</button>
          <button class="btn btn--primary" :disabled="busy || !canSave" @click="save">
            {{ drafting ? 'Save provider' : 'Save changes' }}
          </button>
        </footer>
      </section>

      <div v-else class="form form--empty">
        Select a provider from the list, or add a new one.
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProvidersStore } from '@/stores/providers'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const store = useProvidersStore()

const selected = ref(null)
const drafting = ref(false)
const form = ref(null)
const busy = ref(false)
const saveMsg = ref(null)

const DEFAULT_BASE_URLS = {
  openai:    'https://api.openai.com/v1',
  anthropic: 'https://api.anthropic.com',
  qwen:      'https://dashscope.aliyuncs.com/compatible-mode/v1',
  gemini:    'https://generativelanguage.googleapis.com/v1beta',
  custom:    '',
}
const DEFAULT_MODELS = {
  openai:    'gpt-4o-mini',
  anthropic: 'claude-haiku-4-5',
  qwen:      'qwen-plus',
  gemini:    'gemini-1.5-flash',
  custom:    '',
}

const defaultBaseUrl = computed(() => DEFAULT_BASE_URLS[form.value?.provider_type] || '')
const defaultModel   = computed(() => DEFAULT_MODELS[form.value?.provider_type] || '')
const canSave = computed(() => form.value?.name && form.value?.provider_type && form.value?.api_key)

function blank() {
  return {
    name: '',
    provider_type: 'openai',
    base_url: DEFAULT_BASE_URLS.openai,
    api_key: '',
    default_model: DEFAULT_MODELS.openai,
    fallback_model: '',
    temperature: 0.3,
    max_tokens: 4096,
    multimodal_enabled: true,
  }
}

function applyDefaults() {
  if (!form.value) return
  form.value.base_url = DEFAULT_BASE_URLS[form.value.provider_type] || ''
  form.value.default_model = DEFAULT_MODELS[form.value.provider_type] || ''
}

function startNew() {
  selected.value = null
  drafting.value = true
  form.value = blank()
  saveMsg.value = null
}

function selectExisting(p) {
  drafting.value = false
  selected.value = p
  form.value = {
    name: p.name,
    provider_type: p.provider_type,
    base_url: p.base_url || '',
    api_key: '',
    default_model: p.default_model || '',
    fallback_model: p.fallback_model || '',
    temperature: p.temperature ?? 0.3,
    max_tokens: p.max_tokens ?? 4096,
    multimodal_enabled: !!p.multimodal_enabled,
  }
  saveMsg.value = null
}

function isSelected(p) {
  return !drafting.value && selected.value?.id === p.id
}

async function testConnection() {
  busy.value = true
  try {
    await store.test({
      provider_type: form.value.provider_type,
      api_key: form.value.api_key,
      base_url: form.value.base_url,
      default_model: form.value.default_model,
    })
  } finally {
    busy.value = false
  }
}

async function save() {
  busy.value = true
  saveMsg.value = null
  try {
    const payload = { ...form.value }
    if (drafting.value) {
      await store.save(payload)
      drafting.value = false
      const created = [...store.list].pop()
      if (created) selectExisting(created)
      saveMsg.value = { state: 'ok', text: 'Provider saved.' }
    } else if (selected.value) {
      if (!payload.api_key) delete payload.api_key
      await store.patch(selected.value.id, payload)
      saveMsg.value = { state: 'ok', text: 'Changes saved.' }
    }
  } catch (e) {
    saveMsg.value = { state: 'err', text: e?.message || 'Save failed.' }
  } finally {
    busy.value = false
    setTimeout(() => (saveMsg.value = null), 4000)
  }
}

async function activate() {
  if (!selected.value) return
  busy.value = true
  try { await store.setActive(selected.value.id) }
  finally { busy.value = false }
}

async function remove() {
  if (!selected.value) return
  if (!confirm(`Delete provider "${selected.value.name}"?`)) return
  busy.value = true
  try {
    await store.remove(selected.value.id)
    selected.value = null
    form.value = null
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  await store.loadList()
  if (store.list.length) selectExisting(store.active || store.list[0])
})
</script>

<style scoped>
.prov { display: flex; flex-direction: column; gap: 20px; }

.prov__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.prov__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.prov__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; max-width: 620px; }
.prov__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 6px; max-width: 620px; }

.skeletons { display: flex; flex-direction: column; gap: 12px; }

.layout { display: grid; grid-template-columns: 320px 1fr; gap: 16px; align-items: flex-start; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }

.layout__list { display: flex; flex-direction: column; gap: 8px; }
.card {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 14px; cursor: pointer; border-left: 3px solid transparent;
}
.card:hover { border-color: var(--co-accent); }
.card--on { border-color: var(--co-accent); border-left-color: var(--co-accent); background: var(--co-bg); }
.card--active { border-left-color: #3ecf8e; }
.card--draft { border-style: dashed; }
.card__head { display: flex; justify-content: space-between; align-items: center; }
.card__name { font-family: var(--co-font-mono); font-size: 13px; color: var(--co-text); }
.card__active { font-size: 9px; letter-spacing: 0.15em; color: #3ecf8e; border: 1px solid #3ecf8e; padding: 1px 6px; }
.card__meta { margin-top: 6px; font-size: 11px; color: var(--co-text-dim); text-transform: uppercase; letter-spacing: 0.08em; }
.card__sep { margin: 0 6px; }

.form {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 20px; display: flex; flex-direction: column; gap: 16px;
}
.form--empty { font-size: 12px; color: var(--co-text-dim); text-align: center; padding: 60px 24px; }

.form__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; font-size: 12px; }
.field--wide { grid-column: 1 / -1; }
.field span { color: var(--co-text-dim); letter-spacing: 0.08em; text-transform: uppercase; font-size: 10px; }
.field input, .field select {
  background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); padding: 8px 10px; font-size: 13px;
  font-family: var(--co-font-mono); border-radius: var(--co-radius);
}
.field input:focus, .field select:focus { outline: none; border-color: var(--co-accent); }
.field.check { flex-direction: row; align-items: center; gap: 8px; font-size: 12px; color: var(--co-text-dim); }
.field.check input { width: auto; }

.test {
  padding: 10px 12px; border: 1px solid var(--co-border); font-size: 12px;
  display: flex; gap: 8px; flex-wrap: wrap;
}
.test--ok  { border-color: #3ecf8e; color: #3ecf8e; }
.test--err { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }
.test--info { color: var(--co-text-dim); }

.form__foot { display: flex; gap: 10px; align-items: center; }
.form__spacer { flex: 1; }

.btn {
  padding: 8px 14px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
.btn--danger { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }
.btn--danger:hover { background: var(--co-danger, #ff5469); color: #000; }
</style>
