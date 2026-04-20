<template>
  <section class="seeds">
    <header class="seeds__head">
      <div>
        <span class="seeds__eyebrow">REALITY SEEDS · SIMULATION WORKSPACE</span>
        <h1>Seeds</h1>
        <p>Briefs, documents, and knowledge graphs that feed Reality Seeds simulations.</p>
      </div>
      <router-link :to="{ name: 'SeedCreate' }" class="btn btn--primary">+ New seed</router-link>
    </header>

    <div class="seeds__filters">
      <span class="seeds__filterlabel">STATUS</span>
      <button
        v-for="s in statuses"
        :key="s.value"
        class="chip"
        :class="{ 'chip--on': statusFilter === s.value }"
        @click="statusFilter = s.value"
      >{{ s.label }}</button>
      <input v-model="search" class="seeds__search" placeholder="Search by name or requirement…" />
    </div>

    <div v-if="loading && !entries.length" class="skeletons">
      <LoadingSkeleton v-for="i in 3" :key="i" height="110px" />
    </div>

    <ErrorState
      v-else-if="error"
      title="Couldn't load seeds."
      :body="String(error?.message || error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!filtered.length && !search && statusFilter === 'all'"
      title="No seeds in this workspace."
      body="Seeds are briefs, documents, or knowledge graphs that feed Reality Seeds simulations."
    >
      <router-link :to="{ name: 'SeedCreate' }" class="btn btn--primary">Upload a seed</router-link>
      <router-link to="/app/demo" class="btn btn--ghost">Load demo seed</router-link>
    </EmptyState>

    <EmptyState
      v-else-if="!filtered.length"
      title="No matches."
      body="Try a different status, or clear the search."
    >
      <button class="btn btn--ghost" @click="resetFilters">Clear filters</button>
    </EmptyState>

    <div v-else class="grid">
      <article
        v-for="s in filtered"
        :key="s.id"
        class="card"
        @click="open(s)"
      >
        <header class="card__head">
          <span class="card__status" :class="'card__status--' + (s.status || 'draft')">{{ s.status || 'draft' }}</span>
          <span v-if="s.entities_count" class="card__meta">{{ s.entities_count }} entities</span>
        </header>
        <h2 class="card__name">{{ s.name || s.simulation_id || s.project_id }}</h2>
        <p v-if="s.requirement" class="card__req">{{ trim(s.requirement, 140) }}</p>
        <footer class="card__foot">
          <span>{{ s.files_count || 0 }} file{{ s.files_count === 1 ? '' : 's' }}</span>
          <span v-if="s.current_round != null && s.total_rounds">
            round {{ s.current_round }}/{{ s.total_rounds }}
          </span>
          <span v-if="s.created_at">{{ formatDate(s.created_at) }}</span>
        </footer>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSimulationHistory } from '@/api/simulation'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const router = useRouter()

const entries = ref([])
const loading = ref(false)
const error = ref(null)
const statusFilter = ref('all')
const search = ref('')

const statuses = [
  { value: 'all',       label: 'All' },
  { value: 'completed', label: 'Completed' },
  { value: 'running',   label: 'Running' },
  { value: 'prepared',  label: 'Prepared' },
  { value: 'created',   label: 'Created' },
]

async function reload() {
  loading.value = true
  error.value = null
  try {
    const res = await getSimulationHistory(50)
    const list = res?.data ?? []
    entries.value = list.map((s) => ({
      id: s.simulation_id,
      simulation_id: s.simulation_id,
      project_id: s.project_id,
      name: s.project_name || s.simulation_id,
      requirement: s.simulation_requirement,
      status: s.status,
      entities_count: s.entities_count,
      files_count: (s.files || []).length,
      current_round: s.current_round,
      total_rounds: s.total_rounds,
      created_at: s.created_at,
      updated_at: s.updated_at,
    }))
  } catch (e) {
    error.value = e
    entries.value = []
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return entries.value.filter((s) => {
    if (statusFilter.value !== 'all' && s.status !== statusFilter.value) return false
    if (!q) return true
    return [s.name, s.requirement, s.project_id].filter(Boolean).join(' ').toLowerCase().includes(q)
  })
})

function open(s) { router.push({ name: 'SeedDetail', params: { id: s.simulation_id } }) }
function resetFilters() { statusFilter.value = 'all'; search.value = '' }
function trim(v, n) { return v.length > n ? v.slice(0, n) + '…' : v }
function formatDate(v) {
  if (!v) return ''
  const d = new Date(v)
  return isNaN(d) ? String(v).slice(0, 10) : d.toISOString().slice(0, 10)
}

onMounted(reload)
</script>

<style scoped>
.seeds { display: flex; flex-direction: column; gap: 24px; }

.seeds__head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.seeds__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.seeds__head h1 { font-size: 26px; margin-top: 6px; letter-spacing: -0.01em; }
.seeds__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 4px; max-width: 640px; }

.seeds__filters { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.seeds__filterlabel { font-size: 10px; color: var(--co-text-dim); letter-spacing: 0.15em; margin-right: 4px; }
.chip {
  background: transparent; border: 1px solid var(--co-border-2);
  color: var(--co-text-dim); font-family: var(--co-font-mono);
  font-size: 11px; padding: 5px 10px; cursor: pointer; border-radius: var(--co-radius);
}
.chip:hover { color: var(--co-text); }
.chip--on { color: var(--co-accent); border-color: var(--co-accent); }
.seeds__search {
  flex: 1; min-width: 200px;
  background: var(--co-surface); border: 1px solid var(--co-border-2);
  color: var(--co-text); font-family: var(--co-font-mono);
  padding: 7px 12px; font-size: 12px; border-radius: var(--co-radius);
}
.seeds__search:focus { outline: none; border-color: var(--co-accent); }

.skeletons { display: flex; flex-direction: column; gap: 12px; }

.grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.card {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 18px; cursor: pointer; display: flex; flex-direction: column; gap: 10px;
  transition: border-color 0.15s;
}
.card:hover { border-color: var(--co-accent); }
.card__head { display: flex; justify-content: space-between; align-items: center; }
.card__status {
  font-size: 10px; letter-spacing: 0.12em; padding: 2px 8px;
  border: 1px solid var(--co-border-2); color: var(--co-text-dim);
  text-transform: uppercase;
}
.card__status--running { color: var(--co-accent); border-color: var(--co-accent); }
.card__status--completed { color: #3ecf8e; border-color: #3ecf8e; }
.card__meta { font-size: 11px; color: var(--co-text-dim); }
.card__name { font-size: 16px; letter-spacing: -0.01em; }
.card__req { font-size: 12px; color: var(--co-text-dim); line-height: 1.5; }
.card__foot {
  display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap;
  font-size: 11px; color: var(--co-text-mute, #666);
  border-top: 1px solid var(--co-border); padding-top: 10px; margin-top: auto;
}

.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
