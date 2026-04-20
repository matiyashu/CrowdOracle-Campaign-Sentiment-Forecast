<template>
  <section class="routing">
    <header class="routing__head">
      <div>
        <span class="routing__eyebrow">TASK ROUTING</span>
        <h1>Per-task model choices.</h1>
        <p>Route each task to a specific model. Empty rows fall back to the active provider's default model.</p>
      </div>
      <div class="routing__actions">
        <button class="btn btn--ghost" :disabled="busy" @click="resetAll">Reset all</button>
        <button class="btn btn--primary" :disabled="busy || !dirty" @click="save">Save routing</button>
      </div>
    </header>

    <EmptyState
      v-if="!store.active"
      title="No active provider yet."
      body="Task routing writes to the active provider. Configure one on the Providers tab first."
    >
      <router-link :to="{ name: 'SettingsProviders' }" class="btn btn--primary">Go to providers</router-link>
    </EmptyState>

    <div v-else class="panel">
      <table class="matrix">
        <thead>
          <tr>
            <th>Task</th>
            <th>Model</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in TASKS" :key="t.key">
            <td class="matrix__task">
              <strong>{{ t.label }}</strong>
              <span class="matrix__key">{{ t.key }}</span>
            </td>
            <td>
              <input
                v-model="draft[t.key]"
                :placeholder="`(use default — ${store.active.default_model || 'provider default'})`"
                class="matrix__input"
              />
            </td>
            <td class="matrix__note">{{ t.note }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="saveMsg" class="banner" :class="'banner--' + saveMsg.state">{{ saveMsg.text }}</div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useProvidersStore } from '@/stores/providers'
import EmptyState from '@/components/common/EmptyState.vue'

const store = useProvidersStore()

const TASKS = [
  { key: 'creative_vision', label: 'Creative vision',   note: 'OCR, transcripts, hook extraction.' },
  { key: 'sentiment',       label: 'Sentiment',         note: 'Polarity, emotion, aspect classification.' },
  { key: 'report_writer',   label: 'Report writer',     note: 'Executive summaries and recommendations.' },
  { key: 'simulation',      label: 'Reality Seeds',     note: 'Persona-agent reasoning during simulation.' },
  { key: 'transcript',      label: 'Transcript',        note: 'Audio → text for video creatives.' },
  { key: 'chat',            label: 'Report chat',       note: 'Follow-up Q&A on finished reports.' },
  { key: 'keyword',         label: 'Keyword analysis',  note: 'Phrase extraction and rising-terms detection.' },
  { key: 'impact',          label: 'Impact scoring',    note: 'Cross-signal decomposition and asset scoring.' },
]

const draft = ref({})
const busy = ref(false)
const saveMsg = ref(null)

const dirty = computed(() => {
  const current = store.active?.task_routing || {}
  return TASKS.some((t) => (draft.value[t.key] || '') !== (current[t.key] || ''))
})

function hydrate() {
  const current = store.active?.task_routing || {}
  const next = {}
  for (const t of TASKS) next[t.key] = current[t.key] || ''
  draft.value = next
}

function resetAll() {
  for (const t of TASKS) draft.value[t.key] = ''
}

async function save() {
  busy.value = true
  saveMsg.value = null
  try {
    const payload = {}
    for (const [k, v] of Object.entries(draft.value)) {
      if (v && v.trim()) payload[k] = v.trim()
    }
    await store.saveRouting(payload)
    saveMsg.value = { state: 'ok', text: 'Routing saved to active provider.' }
    hydrate()
  } catch (e) {
    saveMsg.value = { state: 'err', text: e?.message || 'Save failed.' }
  } finally {
    busy.value = false
    setTimeout(() => (saveMsg.value = null), 4000)
  }
}

watch(() => store.active?.id, hydrate)

onMounted(async () => {
  if (!store.list.length) await store.loadList()
  hydrate()
})
</script>

<style scoped>
.routing { display: flex; flex-direction: column; gap: 20px; }

.routing__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.routing__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.routing__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; }
.routing__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 6px; max-width: 620px; }
.routing__actions { display: flex; gap: 10px; }

.panel {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 14px;
}

.matrix { width: 100%; border-collapse: collapse; font-size: 12px; }
.matrix th {
  text-align: left; padding: 8px 10px; color: var(--co-text-dim);
  font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
  border-bottom: 1px solid var(--co-border);
}
.matrix td { padding: 10px; border-bottom: 1px solid var(--co-border); vertical-align: top; }
.matrix__task { display: flex; flex-direction: column; gap: 2px; }
.matrix__task strong { color: var(--co-text); font-size: 13px; }
.matrix__key { font-family: var(--co-font-mono); font-size: 10px; color: var(--co-text-dim); }
.matrix__note { color: var(--co-text-dim); font-size: 11px; line-height: 1.5; max-width: 280px; }
.matrix__input {
  width: 100%; max-width: 360px;
  background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); padding: 7px 10px; font-size: 12px;
  font-family: var(--co-font-mono); border-radius: var(--co-radius);
}
.matrix__input:focus { outline: none; border-color: var(--co-accent); }

.banner { padding: 10px 12px; border: 1px solid var(--co-border); font-size: 12px; }
.banner--ok  { border-color: #3ecf8e; color: #3ecf8e; }
.banner--err { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }

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
</style>
