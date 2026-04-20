<template>
  <div class="seed">
    <header class="seed__head">
      <div class="seed__meta">
        <span class="seed__eyebrow">REALITY SEED · {{ id }}</span>
        <h2 class="seed__name">{{ seedName }}</h2>
        <p v-if="seed?.simulation_requirement" class="seed__req">{{ seed.simulation_requirement }}</p>
      </div>
      <div class="seed__actions">
        <span v-if="seed?.status" class="seed__status" :class="'seed__status--' + seed.status">{{ seed.status }}</span>
        <button class="btn btn--ghost" @click="refreshAll">Refresh</button>
        <router-link
          v-if="seed?.simulation_id"
          :to="{ name: 'SeedRun', params: { runId: seed.simulation_id } }"
          class="btn btn--primary"
        >Open run →</router-link>
      </div>
    </header>

    <nav class="seed__tabs">
      <router-link :to="{ name: 'SeedGraph',     params: { id } }" class="seed__tab">Graph</router-link>
      <router-link :to="{ name: 'SeedSplit',     params: { id } }" class="seed__tab">Split</router-link>
      <router-link :to="{ name: 'SeedWorkbench', params: { id } }" class="seed__tab">Workbench</router-link>
    </nav>

    <ErrorState
      v-if="error"
      title="Couldn't load this seed."
      :body="String(error?.message || error)"
      @retry="refreshAll"
    />

    <div v-else class="seed__body">
      <router-view
        :graph-data="graphData"
        :loading="loading"
        :current-phase="currentPhase"
        :is-simulating="isSimulating"
        :documents="documents"
        :actions="actions"
        :messages="messages"
        :log="log"
        :sending="sending"
        @refresh="refreshAll"
        @toggle-maximize="toggleMax"
        @send-message="sendMessage"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getSimulation, getRunStatusDetail, getSimulationActions } from '@/api/simulation'
import { getGraphData } from '@/api/graph'
import { chatWithReport } from '@/api/report'
import ErrorState from '@/components/common/ErrorState.vue'

const props = defineProps({ id: { type: String, required: true } })

const seed = ref(null)
const graphData = ref(null)
const actions = ref([])
const messages = ref([])
const log = ref('')
const loading = ref(false)
const sending = ref(false)
const error = ref(null)
const currentPhase = ref(0)
const isSimulating = ref(false)

let pollHandle = null

const seedName = computed(() => seed.value?.project_name || seed.value?.simulation_id || props.id)
const documents = computed(() => seed.value?.files || [])

async function loadSeed() {
  loading.value = true
  error.value = null
  try {
    const sim = await getSimulation(props.id)
    seed.value = sim?.data ?? sim
    isSimulating.value = seed.value?.status === 'running'
    currentPhase.value = seed.value?.current_round || 0
    if (seed.value?.graph_id) {
      const g = await getGraphData(seed.value.graph_id)
      graphData.value = g?.data ?? g
    }
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
}

async function loadActions() {
  try {
    const res = await getSimulationActions(props.id, { limit: 100 })
    actions.value = res?.data?.actions || res?.actions || []
  } catch { /* non-fatal */ }
}

async function loadRunStatus() {
  try {
    const res = await getRunStatusDetail(props.id)
    const d = res?.data ?? res
    isSimulating.value = d?.status === 'running'
    if (typeof d?.current_round === 'number') currentPhase.value = d.current_round
    if (d?.log) log.value = d.log
  } catch { /* non-fatal */ }
}

function startPolling() {
  stopPolling()
  pollHandle = setInterval(() => {
    if (isSimulating.value) { loadRunStatus(); loadActions() }
  }, 4000)
}
function stopPolling() {
  if (pollHandle) { clearInterval(pollHandle); pollHandle = null }
}

async function refreshAll() {
  await loadSeed()
  await Promise.all([loadActions(), loadRunStatus()])
}

function toggleMax() { /* reserved for fullscreen graph */ }

async function sendMessage(text) {
  if (!text) return
  messages.value.push({ role: 'user', content: text })
  sending.value = true
  try {
    const res = await chatWithReport({
      simulation_id: props.id,
      message: text,
      chat_history: messages.value.slice(0, -1),
    })
    const reply = res?.data?.reply || res?.reply || ''
    if (reply) messages.value.push({ role: 'assistant', content: reply })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `Error: ${e?.message || e}` })
  } finally {
    sending.value = false
  }
}

watch(isSimulating, (on) => (on ? startPolling() : stopPolling()))
watch(() => props.id, refreshAll)

onMounted(refreshAll)
onBeforeUnmount(stopPolling)
</script>

<style scoped>
.seed { display: flex; flex-direction: column; gap: 18px; }

.seed__head {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 16px; flex-wrap: wrap;
}
.seed__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.seed__name { font-size: 20px; margin-top: 6px; letter-spacing: -0.01em; }
.seed__req { color: var(--co-text-dim); font-size: 12px; margin-top: 4px; max-width: 720px; }
.seed__actions { display: flex; align-items: center; gap: 10px; }
.seed__status {
  font-size: 10px; letter-spacing: 0.12em; padding: 3px 10px;
  border: 1px solid var(--co-border-2); color: var(--co-text-dim);
  text-transform: uppercase;
}
.seed__status--running { color: var(--co-accent); border-color: var(--co-accent); }
.seed__status--completed { color: #3ecf8e; border-color: #3ecf8e; }

.seed__tabs { display: flex; gap: 0; border-bottom: 1px solid var(--co-border); }
.seed__tab {
  padding: 10px 16px; font-size: 12px; color: var(--co-text-dim);
  font-family: var(--co-font-mono); border-bottom: 2px solid transparent;
  margin-bottom: -1px; text-transform: uppercase; letter-spacing: 0.1em;
}
.seed__tab:hover { color: var(--co-text); }
.seed__tab.router-link-active { color: var(--co-accent); border-color: var(--co-accent); }

.seed__body { min-height: 560px; }

.btn {
  padding: 7px 14px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
