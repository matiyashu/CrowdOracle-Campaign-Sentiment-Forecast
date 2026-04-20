<template>
  <section class="run">
    <header class="run__head">
      <div>
        <span class="run__eyebrow">SIMULATION RUN · {{ runId }}</span>
        <h2>{{ runName }}</h2>
        <p v-if="requirement" class="run__req">{{ requirement }}</p>
      </div>
      <div class="run__actions">
        <span class="run__status" :class="'run__status--' + (status || 'idle')">{{ status || 'idle' }}</span>
        <button class="btn btn--ghost" @click="refresh">Refresh</button>
        <button
          v-if="status === 'running'"
          class="btn btn--danger"
          :disabled="busy"
          @click="stop"
        >Stop run</button>
        <button
          v-else
          class="btn btn--primary"
          :disabled="busy"
          @click="start"
        >Start run</button>
      </div>
    </header>

    <ErrorState
      v-if="error"
      title="Couldn't load run status."
      :body="String(error?.message || error)"
      @retry="refresh"
    />

    <div v-else-if="loading && !detail" class="skeletons">
      <LoadingSkeleton v-for="i in 3" :key="i" height="120px" />
    </div>

    <template v-else>
      <section class="stats">
        <div class="stat">
          <span>Round</span>
          <strong>{{ currentRound }} / {{ totalRounds || '—' }}</strong>
        </div>
        <div class="stat">
          <span>Active agents</span>
          <strong>{{ activeAgents ?? '—' }}</strong>
        </div>
        <div class="stat">
          <span>Posts generated</span>
          <strong>{{ postCount ?? '—' }}</strong>
        </div>
        <div class="stat">
          <span>Platform</span>
          <strong>{{ platform || '—' }}</strong>
        </div>
      </section>

      <section class="panel">
        <header class="panel__head">
          <h3>Recent agent actions</h3>
          <span class="panel__sub">{{ actions.length }} action{{ actions.length === 1 ? '' : 's' }}</span>
        </header>
        <div v-if="!actions.length" class="panel__empty">No actions recorded yet.</div>
        <ul v-else class="actions">
          <li v-for="(a, i) in actions.slice(0, 60)" :key="a.id || i" class="actions__row">
            <span class="actions__round">r{{ a.round_num ?? '?' }}</span>
            <span class="actions__agent">{{ a.agent_name || `agent ${a.agent_id}` }}</span>
            <span class="actions__kind">{{ a.action_type || a.action || '—' }}</span>
            <span v-if="a.content" class="actions__content">{{ trim(a.content, 160) }}</span>
          </li>
        </ul>
      </section>

      <section v-if="log" class="panel">
        <header class="panel__head"><h3>Run log</h3></header>
        <pre class="log">{{ log }}</pre>
      </section>
    </template>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getRunStatusDetail, getSimulationActions, startSimulation, stopSimulation, getSimulation } from '@/api/simulation'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const props = defineProps({ runId: { type: String, required: true } })

const detail = ref(null)
const meta = ref(null)
const actions = ref([])
const loading = ref(false)
const busy = ref(false)
const error = ref(null)

let pollHandle = null

const status = computed(() => detail.value?.status || meta.value?.status)
const currentRound = computed(() => detail.value?.current_round ?? meta.value?.current_round ?? 0)
const totalRounds = computed(() => detail.value?.total_rounds ?? meta.value?.total_rounds)
const activeAgents = computed(() => detail.value?.active_agent_count ?? detail.value?.agent_count)
const postCount = computed(() => detail.value?.post_count ?? detail.value?.total_posts)
const platform = computed(() => detail.value?.platform || meta.value?.platform)
const log = computed(() => detail.value?.log || '')
const runName = computed(() => meta.value?.project_name || meta.value?.simulation_id || props.runId)
const requirement = computed(() => meta.value?.simulation_requirement)

async function refresh() {
  loading.value = true
  error.value = null
  try {
    const [m, d] = await Promise.all([
      getSimulation(props.runId).catch(() => null),
      getRunStatusDetail(props.runId).catch(() => null),
    ])
    meta.value = m?.data ?? m ?? meta.value
    detail.value = d?.data ?? d ?? detail.value
    loadActions()
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
}

async function loadActions() {
  try {
    const res = await getSimulationActions(props.runId, { limit: 120 })
    actions.value = res?.data?.actions || res?.actions || []
  } catch { /* non-fatal */ }
}

async function start() {
  busy.value = true
  try {
    await startSimulation({ simulation_id: props.runId })
    await refresh()
  } catch (e) {
    error.value = e
  } finally {
    busy.value = false
  }
}

async function stop() {
  busy.value = true
  try {
    await stopSimulation({ simulation_id: props.runId })
    await refresh()
  } catch (e) {
    error.value = e
  } finally {
    busy.value = false
  }
}

function trim(v, n) { return v.length > n ? v.slice(0, n) + '…' : v }

function startPolling() {
  stopPolling()
  pollHandle = setInterval(refresh, 4000)
}
function stopPolling() {
  if (pollHandle) { clearInterval(pollHandle); pollHandle = null }
}

watch(status, (s) => {
  if (s === 'running') startPolling()
  else stopPolling()
})

watch(() => props.runId, refresh)

onMounted(refresh)
onBeforeUnmount(stopPolling)
</script>

<style scoped>
.run { display: flex; flex-direction: column; gap: 20px; }

.run__head {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 16px; flex-wrap: wrap;
}
.run__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.run__head h2 { font-size: 20px; margin-top: 6px; letter-spacing: -0.01em; }
.run__req { color: var(--co-text-dim); font-size: 12px; margin-top: 4px; max-width: 720px; }

.run__actions { display: flex; gap: 10px; align-items: center; }
.run__status {
  font-size: 10px; letter-spacing: 0.12em; padding: 4px 10px;
  border: 1px solid var(--co-border-2); color: var(--co-text-dim);
  text-transform: uppercase;
}
.run__status--running { color: var(--co-accent); border-color: var(--co-accent); }
.run__status--completed { color: #3ecf8e; border-color: #3ecf8e; }
.run__status--failed { color: var(--co-danger, #ff5469); border-color: var(--co-danger, #ff5469); }

.skeletons { display: flex; flex-direction: column; gap: 12px; }

.stats {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.stat {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 4px;
}
.stat span { font-size: 11px; letter-spacing: 0.12em; color: var(--co-text-dim); text-transform: uppercase; }
.stat strong { font-size: 22px; color: var(--co-text); letter-spacing: -0.01em; }

.panel {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.panel__head { display: flex; justify-content: space-between; align-items: center; }
.panel__head h3 { font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--co-text-dim); }
.panel__sub { font-size: 11px; color: var(--co-text-dim); }
.panel__empty { font-size: 12px; color: var(--co-text-mute, #666); padding: 18px 0; text-align: center; }

.actions { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; font-size: 11px; }
.actions__row {
  display: grid; grid-template-columns: 40px 140px 80px 1fr; gap: 10px;
  padding: 6px 0; border-bottom: 1px dashed var(--co-border);
}
.actions__round { color: var(--co-text-dim); font-family: var(--co-font-mono); }
.actions__agent { color: var(--co-text); }
.actions__kind {
  font-size: 10px; color: var(--co-accent); text-transform: uppercase;
  letter-spacing: 0.05em;
}
.actions__content { color: var(--co-text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.log {
  font-family: var(--co-font-mono); font-size: 11px; line-height: 1.5;
  color: var(--co-text); white-space: pre-wrap; margin: 0;
  background: var(--co-bg); padding: 12px; border: 1px solid var(--co-border);
  max-height: 320px; overflow: auto;
}

.btn {
  padding: 7px 14px; font-family: var(--co-font-mono); font-size: 12px;
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
