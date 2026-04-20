<template>
  <section class="browser">
    <header class="browser__head">
      <div>
        <span class="browser__eyebrow">CROSS-PROJECT GRAPH · GOD'S-EYE VIEW</span>
        <h1>Graph browser</h1>
        <p>
          Every knowledge graph in the workspace. Pick a project on the left to inspect its
          entities, relationships, and evidence — or load a demo package to see the universe
          Coastline would see.
        </p>
      </div>
      <button class="btn btn--ghost" :disabled="loadingList" @click="reloadProjects">
        {{ loadingList ? 'Loading…' : 'Refresh' }}
      </button>
    </header>

    <ErrorState
      v-if="listError"
      title="Couldn't load graphs."
      :body="String(listError?.message || listError)"
      @retry="reloadProjects"
    />

    <div v-else-if="loadingList && !projects.length" class="skeletons">
      <LoadingSkeleton height="420px" />
    </div>

    <EmptyState
      v-else-if="!projectsWithGraph.length"
      title="No graphs yet."
      body="Load a demo package or upload a seed to see the cross-project graph."
    >
      <router-link to="/app/demo" class="btn btn--primary">Load demo package</router-link>
      <router-link :to="{ name: 'SeedCreate' }" class="btn btn--ghost">Upload a seed</router-link>
    </EmptyState>

    <div v-else class="browser__body">
      <aside class="rail">
        <div class="rail__label">PROJECTS · {{ projectsWithGraph.length }}</div>
        <button
          v-for="p in projectsWithGraph"
          :key="p.project_id"
          class="rail__item"
          :class="{ 'rail__item--active': selectedId === p.project_id }"
          @click="selectProject(p)"
        >
          <span class="rail__name">{{ p.name || p.project_id }}</span>
          <span class="rail__meta">
            <span class="rail__dot" :class="'rail__dot--' + (p.status || 'created')"></span>
            <span>{{ (p.status || '').replace('_', ' ') || '—' }}</span>
          </span>
          <span v-if="isDemo(p)" class="rail__pill">demo</span>
        </button>
      </aside>

      <main class="pane">
        <div class="pane__head">
          <div>
            <span class="pane__eyebrow">{{ selected?.graph_id || '—' }}</span>
            <h2>{{ selected?.name || 'Select a graph' }}</h2>
          </div>
          <span v-if="graphData" class="pane__stats">
            {{ graphData.nodes?.length || 0 }} nodes · {{ graphData.edges?.length || 0 }} edges
          </span>
        </div>

        <ErrorState
          v-if="graphError"
          title="Couldn't load this graph."
          :body="String(graphError?.message || graphError)"
          @retry="() => selected && loadGraph(selected)"
        />

        <div v-else-if="loadingGraph" class="pane__loading">
          <LoadingSkeleton height="480px" />
        </div>

        <div v-else class="pane__graph">
          <GraphPanel
            :graph-data="graphData"
            :loading="loadingGraph"
            :current-phase="0"
            :is-simulating="false"
          />
        </div>
      </main>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listProjects, getGraphData } from '@/api/graph'
import GraphPanel from '@/components/realityseeds/GraphPanel.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const projects = ref([])
const selectedId = ref(null)
const graphData = ref(null)
const loadingList = ref(false)
const loadingGraph = ref(false)
const listError = ref(null)
const graphError = ref(null)

const projectsWithGraph = computed(() =>
  projects.value.filter(p => p.graph_id)
)

const selected = computed(() =>
  projectsWithGraph.value.find(p => p.project_id === selectedId.value) || null
)

function isDemo(p) {
  return (p.project_id || '').startsWith('proj_demo_') || (p.graph_id || '').startsWith('demo_graph_')
}

function pickInitial() {
  if (!projectsWithGraph.value.length) return null
  return projectsWithGraph.value.find(isDemo) || projectsWithGraph.value[0]
}

async function reloadProjects() {
  loadingList.value = true
  listError.value = null
  try {
    const res = await listProjects(50)
    projects.value = Array.isArray(res?.data) ? res.data : []
    const initial = pickInitial()
    if (initial) await selectProject(initial)
    else { selectedId.value = null; graphData.value = null }
  } catch (e) {
    listError.value = e
    projects.value = []
  } finally {
    loadingList.value = false
  }
}

async function selectProject(p) {
  selectedId.value = p.project_id
  await loadGraph(p)
}

async function loadGraph(p) {
  if (!p?.graph_id) { graphData.value = null; return }
  loadingGraph.value = true
  graphError.value = null
  graphData.value = null
  try {
    const res = await getGraphData(p.graph_id)
    graphData.value = res?.data || null
  } catch (e) {
    graphError.value = e
  } finally {
    loadingGraph.value = false
  }
}

onMounted(reloadProjects)
</script>

<style scoped>
.browser { display: flex; flex-direction: column; gap: 18px; }
.browser__head {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 16px; flex-wrap: wrap;
}
.browser__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.browser__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; }
.browser__head p { font-size: 13px; color: var(--co-text-dim); margin-top: 4px; max-width: 720px; line-height: 1.55; }

.skeletons { display: flex; flex-direction: column; gap: 12px; }

.browser__body {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  min-height: 600px;
}

.rail {
  display: flex; flex-direction: column; gap: 4px;
  border: 1px solid var(--co-border); background: var(--co-surface);
  padding: 12px; max-height: 720px; overflow-y: auto;
}
.rail__label {
  font-size: 10px; letter-spacing: 0.15em; color: var(--co-text-dim);
  padding: 4px 6px 10px;
}
.rail__item {
  text-align: left; background: transparent; border: 1px solid transparent;
  color: var(--co-text); font-family: inherit; cursor: pointer;
  padding: 10px 10px; display: flex; flex-direction: column; gap: 6px;
  border-radius: var(--co-radius);
  position: relative;
}
.rail__item:hover { background: rgba(255,255,255,0.04); }
.rail__item--active {
  background: rgba(255,106,0,0.08);
  border-color: var(--co-accent);
}
.rail__name { font-size: 13px; color: var(--co-text); }
.rail__meta { font-size: 11px; color: var(--co-text-dim); display: flex; gap: 6px; align-items: center; }
.rail__dot { width: 6px; height: 6px; border-radius: 50%; background: var(--co-border-2); display: inline-block; }
.rail__dot--graph_completed { background: #3ecf8e; }
.rail__dot--graph_building,
.rail__dot--ontology_generated { background: var(--co-accent); }
.rail__dot--failed { background: var(--co-danger, #ff5469); }
.rail__pill {
  position: absolute; top: 8px; right: 8px;
  font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--co-accent); border: 1px solid var(--co-accent);
  padding: 1px 6px;
}

.pane {
  border: 1px solid var(--co-border); background: var(--co-surface);
  display: flex; flex-direction: column; min-height: 600px;
}
.pane__head {
  padding: 14px 18px; border-bottom: 1px solid var(--co-border);
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 12px; flex-wrap: wrap;
}
.pane__eyebrow {
  font-size: 10px; letter-spacing: 0.1em; color: var(--co-text-dim);
  font-family: var(--co-font-mono);
}
.pane__head h2 { font-size: 15px; letter-spacing: -0.01em; margin-top: 4px; }
.pane__stats { font-size: 11px; color: var(--co-text-dim); font-family: var(--co-font-mono); }
.pane__loading { padding: 18px; }
.pane__graph { flex: 1; min-height: 560px; position: relative; }

.btn {
  padding: 7px 12px; font-family: var(--co-font-mono); font-size: 11px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2, var(--co-accent)); color: #000; }
.btn--ghost { background: transparent; }

@media (max-width: 960px) {
  .browser__body { grid-template-columns: 1fr; }
  .rail { max-height: 280px; }
}
</style>
