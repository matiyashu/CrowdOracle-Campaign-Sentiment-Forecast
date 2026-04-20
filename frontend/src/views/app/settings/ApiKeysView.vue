<template>
  <section class="keys">
    <header class="keys__head">
      <span class="keys__eyebrow">EXTERNAL API KEYS</span>
      <h1>Third-party data sources.</h1>
      <p>Credentials for mention ingestion, social listening, and trend APIs. Stored locally in this browser for now — backend persistence ships with the paid plans.</p>
    </header>

    <div class="banner banner--warn">
      Beta · Keys are saved to your browser's local storage only. Do not use production credentials on shared machines.
    </div>

    <table class="table">
      <thead>
        <tr>
          <th>Service</th>
          <th>Status</th>
          <th>Key</th>
          <th class="right">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in SERVICES" :key="s.key">
          <td class="table__svc">
            <strong>{{ s.label }}</strong>
            <span class="muted">{{ s.note }}</span>
          </td>
          <td>
            <span class="pill" :class="stored[s.key] ? 'pill--on' : 'pill--off'">
              {{ stored[s.key] ? 'Connected' : 'Not set' }}
            </span>
          </td>
          <td class="table__key">
            <code v-if="stored[s.key]">{{ mask(stored[s.key]) }}</code>
            <span v-else class="muted">—</span>
          </td>
          <td class="right">
            <button class="btn btn--ghost" @click="edit(s)">{{ stored[s.key] ? 'Update' : 'Add key' }}</button>
            <button v-if="stored[s.key]" class="btn btn--danger" @click="clear(s.key)">Clear</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editing" class="drawer">
      <header class="drawer__head">
        <strong>{{ editing.label }}</strong>
        <button class="btn btn--ghost" @click="editing = null">Cancel</button>
      </header>
      <p class="muted">{{ editing.help }}</p>
      <label class="field">
        <span>API key</span>
        <input v-model="draft" type="password" autocomplete="new-password" :placeholder="editing.placeholder" />
      </label>
      <footer class="drawer__foot">
        <span class="spacer"></span>
        <button class="btn btn--primary" :disabled="!draft" @click="commit">Save key</button>
      </footer>
    </div>

    <div v-if="saveMsg" class="banner" :class="'banner--' + saveMsg.state">{{ saveMsg.text }}</div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const SERVICES = [
  { key: 'x',            label: 'X (Twitter) API',  note: 'Mention ingestion and timeline pulls.',
    help: 'Bearer token from the X developer portal.',
    placeholder: 'AAAA…' },
  { key: 'reddit',       label: 'Reddit API',       note: 'Subreddit & thread mention mining.',
    help: 'OAuth2 client secret in the form "client_id:client_secret".',
    placeholder: 'clientId:secret' },
  { key: 'brandwatch',   label: 'Brandwatch',       note: 'Enterprise listening feeds.',
    help: 'Project API key from Brandwatch dashboard.',
    placeholder: 'bw_…' },
  { key: 'meltwater',    label: 'Meltwater',        note: 'Premium news & social mentions.',
    help: 'Personal API key from Meltwater settings.',
    placeholder: 'mw_…' },
  { key: 'google_trends', label: 'Google Trends',   note: 'Query-volume context for keywords.',
    help: 'SerpAPI key (Google Trends access).',
    placeholder: 'sk-…' },
]

const STORAGE_KEY = 'crowdoracle.external_keys'
const stored = ref({})
const editing = ref(null)
const draft = ref('')
const saveMsg = ref(null)

function load() {
  try { stored.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') }
  catch { stored.value = {} }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stored.value))
}

function mask(v) {
  if (!v) return ''
  if (v.length <= 8) return '•'.repeat(v.length)
  return v.slice(0, 4) + '•'.repeat(8) + v.slice(-4)
}

function edit(s) {
  editing.value = s
  draft.value = stored.value[s.key] || ''
}

function commit() {
  if (!editing.value || !draft.value) return
  stored.value = { ...stored.value, [editing.value.key]: draft.value }
  persist()
  saveMsg.value = { state: 'ok', text: `${editing.value.label} key saved.` }
  editing.value = null
  draft.value = ''
  setTimeout(() => (saveMsg.value = null), 3500)
}

function clear(key) {
  const next = { ...stored.value }
  delete next[key]
  stored.value = next
  persist()
}

onMounted(load)
</script>

<style scoped>
.keys { display: flex; flex-direction: column; gap: 20px; }
.keys__head { display: flex; flex-direction: column; gap: 6px; max-width: 720px; }
.keys__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.keys__head h1 { font-size: 22px; letter-spacing: -0.01em; }
.keys__head p { font-size: 13px; color: var(--co-text-dim); line-height: 1.5; }

.banner { padding: 10px 12px; border: 1px solid var(--co-border); font-size: 12px; }
.banner--warn { border-color: var(--co-accent); color: var(--co-accent); }
.banner--ok   { border-color: #3ecf8e; color: #3ecf8e; }
.banner--err  { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }

.table {
  width: 100%; border-collapse: collapse;
  background: var(--co-surface); border: 1px solid var(--co-border);
  font-size: 12px;
}
.table th {
  text-align: left; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--co-text-dim); padding: 10px 14px; border-bottom: 1px solid var(--co-border);
}
.table th.right, .table td.right { text-align: right; }
.table td { padding: 12px 14px; border-bottom: 1px solid var(--co-border); }
.table__svc strong { display: block; color: var(--co-text); font-size: 13px; }
.table__svc .muted { font-size: 11px; }
.table__key code { font-family: var(--co-font-mono); font-size: 11px; color: var(--co-text); }

.pill {
  font-size: 10px; letter-spacing: 0.1em; padding: 2px 8px;
  border: 1px solid var(--co-border-2); color: var(--co-text-dim);
  text-transform: uppercase;
}
.pill--on  { color: #3ecf8e; border-color: #3ecf8e; }
.pill--off { color: var(--co-text-dim); }

.muted { color: var(--co-text-dim); font-size: 11px; }

.drawer {
  background: var(--co-surface); border: 1px solid var(--co-accent);
  padding: 18px; display: flex; flex-direction: column; gap: 12px;
}
.drawer__head { display: flex; justify-content: space-between; align-items: center; }
.drawer__foot { display: flex; gap: 10px; align-items: center; }
.spacer { flex: 1; }

.field { display: flex; flex-direction: column; gap: 4px; font-size: 12px; }
.field span { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--co-text-dim); }
.field input {
  background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); padding: 8px 10px; font-size: 13px;
  font-family: var(--co-font-mono); border-radius: var(--co-radius);
}
.field input:focus { outline: none; border-color: var(--co-accent); }

.btn {
  padding: 7px 12px; font-family: var(--co-font-mono); font-size: 11px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
  margin-left: 6px;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
.btn--danger { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }
.btn--danger:hover { background: var(--co-danger, #ff5469); color: #000; }
</style>
