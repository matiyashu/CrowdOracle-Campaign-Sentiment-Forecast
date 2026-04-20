<template>
  <section class="ws">
    <header class="ws__head">
      <span class="ws__eyebrow">WORKSPACE</span>
      <h1>Workspace preferences</h1>
      <p>Locale, time zone, theme, and defaults for new tasks.</p>
    </header>

    <div class="grid">
      <section class="card">
        <header class="card__head">
          <h3>Language</h3>
          <span class="card__sub">Affects app copy and locale-aware formatting.</span>
        </header>
        <div class="row">
          <label v-for="l in LOCALES" :key="l.code" class="chip" :class="{ 'chip--on': locale === l.code }">
            <input type="radio" :value="l.code" v-model="locale" />
            <span>{{ l.label }}</span>
          </label>
        </div>
      </section>

      <section class="card">
        <header class="card__head">
          <h3>Theme</h3>
          <span class="card__sub">Dark is built-in. Light is on the roadmap.</span>
        </header>
        <div class="row">
          <label class="chip chip--on">
            <input type="radio" value="dark" checked disabled />
            <span>Dark (default)</span>
          </label>
          <label class="chip chip--disabled">
            <input type="radio" value="light" disabled />
            <span>Light — coming soon</span>
          </label>
        </div>
      </section>

      <section class="card">
        <header class="card__head">
          <h3>Time zone</h3>
          <span class="card__sub">Used for chart axes and KPI deltas.</span>
        </header>
        <div class="row">
          <select v-model="timeZone" class="select">
            <option v-for="tz in TIME_ZONES" :key="tz" :value="tz">{{ tz }}</option>
          </select>
          <span class="muted">Detected: {{ detectedTz }}</span>
        </div>
      </section>

      <section class="card">
        <header class="card__head">
          <h3>Default AI provider</h3>
          <span class="card__sub">Used when a task doesn't have a routing override.</span>
        </header>
        <div class="row">
          <select v-model="defaultProvider" class="select" :disabled="!providers.list.length">
            <option value="">(use active provider)</option>
            <option v-for="p in providers.list" :key="p.id" :value="p.id">
              {{ p.name }} — {{ p.provider_type }}
            </option>
          </select>
          <router-link :to="{ name: 'SettingsProviders' }" class="muted link">
            Manage providers →
          </router-link>
        </div>
      </section>

      <section class="card">
        <header class="card__head">
          <h3>Auto-analyze on upload</h3>
          <span class="card__sub">Kick off creative vision tasks as soon as assets are uploaded.</span>
        </header>
        <div class="row">
          <label class="toggle">
            <input type="checkbox" v-model="autoAnalyze" />
            <span>{{ autoAnalyze ? 'Enabled' : 'Disabled' }}</span>
          </label>
        </div>
      </section>
    </div>

    <footer class="ws__foot">
      <span v-if="saveMsg" class="banner" :class="'banner--' + saveMsg.state">{{ saveMsg.text }}</span>
      <span class="spacer"></span>
      <button class="btn btn--ghost" @click="reset">Reset</button>
      <button class="btn btn--primary" :disabled="!dirty" @click="save">Save preferences</button>
    </footer>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProvidersStore } from '@/stores/providers'

const { locale: i18nLocale } = useI18n()
const providers = useProvidersStore()

const LOCALES = [
  { code: 'en', label: 'English' },
  { code: 'id', label: 'Bahasa Indonesia' },
  { code: 'zh', label: '中文' },
]

const TIME_ZONES = [
  'UTC',
  'America/Los_Angeles', 'America/New_York', 'America/Chicago', 'America/Sao_Paulo',
  'Europe/London', 'Europe/Berlin', 'Europe/Paris', 'Europe/Istanbul',
  'Africa/Cairo', 'Asia/Dubai', 'Asia/Kolkata', 'Asia/Jakarta',
  'Asia/Shanghai', 'Asia/Singapore', 'Asia/Tokyo', 'Australia/Sydney',
]

const STORAGE_KEY = 'crowdoracle.workspace'
const detectedTz = Intl?.DateTimeFormat?.().resolvedOptions?.()?.timeZone || 'UTC'

const locale = ref('en')
const timeZone = ref(detectedTz)
const defaultProvider = ref('')
const autoAnalyze = ref(true)
const snapshot = ref(null)
const saveMsg = ref(null)

const dirty = computed(() => {
  if (!snapshot.value) return false
  return (
    locale.value !== snapshot.value.locale ||
    timeZone.value !== snapshot.value.timeZone ||
    defaultProvider.value !== snapshot.value.defaultProvider ||
    autoAnalyze.value !== snapshot.value.autoAnalyze
  )
})

function currentState() {
  return {
    locale: locale.value,
    timeZone: timeZone.value,
    defaultProvider: defaultProvider.value,
    autoAnalyze: autoAnalyze.value,
  }
}

function load() {
  let stored = {}
  try { stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') } catch { /* ignore */ }
  locale.value = stored.locale || i18nLocale.value || 'en'
  timeZone.value = stored.timeZone || detectedTz
  defaultProvider.value = stored.defaultProvider || ''
  autoAnalyze.value = stored.autoAnalyze ?? true
  snapshot.value = currentState()
}

function reset() {
  if (!snapshot.value) return
  locale.value = snapshot.value.locale
  timeZone.value = snapshot.value.timeZone
  defaultProvider.value = snapshot.value.defaultProvider
  autoAnalyze.value = snapshot.value.autoAnalyze
}

function save() {
  const state = currentState()
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  i18nLocale.value = state.locale
  snapshot.value = state
  saveMsg.value = { state: 'ok', text: 'Preferences saved.' }
  setTimeout(() => (saveMsg.value = null), 3500)
}

onMounted(async () => {
  if (!providers.list.length) await providers.loadList()
  load()
})
</script>

<style scoped>
.ws { display: flex; flex-direction: column; gap: 20px; }
.ws__head { display: flex; flex-direction: column; gap: 6px; max-width: 620px; }
.ws__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.ws__head h1 { font-size: 22px; letter-spacing: -0.01em; }
.ws__head p { font-size: 13px; color: var(--co-text-dim); }

.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }

.card {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.card__head { display: flex; flex-direction: column; gap: 4px; }
.card__head h3 { font-size: 13px; letter-spacing: 0.05em; }
.card__sub { font-size: 11px; color: var(--co-text-dim); }

.row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.muted { font-size: 11px; color: var(--co-text-dim); }
.link { color: var(--co-accent); }
.link:hover { color: var(--co-accent-2); }

.chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border: 1px solid var(--co-border-2);
  font-size: 12px; color: var(--co-text-dim); cursor: pointer;
  font-family: var(--co-font-mono); border-radius: var(--co-radius);
}
.chip input { display: none; }
.chip:hover { color: var(--co-text); }
.chip--on { color: var(--co-accent); border-color: var(--co-accent); }
.chip--disabled { opacity: 0.5; cursor: not-allowed; }

.select {
  background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); padding: 7px 10px; font-size: 12px;
  font-family: var(--co-font-mono); border-radius: var(--co-radius);
  min-width: 240px;
}
.select:focus { outline: none; border-color: var(--co-accent); }

.toggle {
  display: inline-flex; gap: 8px; align-items: center;
  font-size: 12px; color: var(--co-text); cursor: pointer;
}

.ws__foot { display: flex; gap: 10px; align-items: center; padding-top: 8px; border-top: 1px solid var(--co-border); }
.spacer { flex: 1; }
.banner { padding: 6px 12px; border: 1px solid var(--co-border); font-size: 12px; }
.banner--ok { border-color: #3ecf8e; color: #3ecf8e; }
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
