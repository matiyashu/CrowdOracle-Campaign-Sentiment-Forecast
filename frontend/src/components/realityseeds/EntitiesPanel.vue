<template>
  <div class="entities">
    <header class="entities__head">
      <div>
        <span class="entities__eyebrow">GRAPH ENTITIES</span>
        <h3>{{ totalCount }} entit{{ totalCount === 1 ? 'y' : 'ies' }} across {{ groups.length }} type{{ groups.length === 1 ? '' : 's' }}</h3>
      </div>
      <div class="entities__filters">
        <input
          v-model="query"
          class="entities__search"
          placeholder="Search by name, label, or fact…"
        />
        <select v-model="typeFilter" class="entities__select">
          <option value="">All types</option>
          <option v-for="g in groups" :key="g.name" :value="g.name">{{ g.name }} ({{ g.items.length }})</option>
        </select>
      </div>
    </header>

    <div v-if="!graphData" class="entities__empty">No graph loaded yet.</div>
    <div v-else-if="!filteredGroups.length" class="entities__empty">No entities match your filter.</div>

    <div v-else class="entities__groups">
      <section v-for="g in filteredGroups" :key="g.name" class="group">
        <header class="group__head">
          <span class="group__dot" :style="{ background: g.color }"></span>
          <h4>{{ g.name }}</h4>
          <span class="group__count">{{ g.items.length }}</span>
        </header>
        <ul class="cards">
          <li
            v-for="n in g.items"
            :key="n.uuid"
            class="card"
            :class="{ 'card--on': selected?.uuid === n.uuid }"
            @click="select(n)"
          >
            <div class="card__head">
              <span class="card__name">{{ n.name }}</span>
              <span class="card__labels">{{ (n.labels || []).filter(l => l !== 'Entity').join(' · ') || '—' }}</span>
            </div>
            <p v-if="n.summary" class="card__summary">{{ n.summary }}</p>
          </li>
        </ul>
      </section>
    </div>

    <aside v-if="selected" class="drawer">
      <header class="drawer__head">
        <div>
          <span class="drawer__eyebrow">ENTITY · {{ selected.uuid }}</span>
          <h3>{{ selected.name }}</h3>
        </div>
        <button class="drawer__close" @click="selected = null">×</button>
      </header>
      <dl class="drawer__fields">
        <div v-if="(selected.labels || []).length">
          <dt>Labels</dt>
          <dd>{{ (selected.labels || []).join(', ') }}</dd>
        </div>
        <div v-if="selected.summary">
          <dt>Summary</dt>
          <dd>{{ selected.summary }}</dd>
        </div>
        <div v-if="selected.attributes && Object.keys(selected.attributes).length">
          <dt>Attributes</dt>
          <dd>
            <ul class="attrs">
              <li v-for="(v, k) in selected.attributes" :key="k">
                <span class="attrs__key">{{ k }}</span>
                <span class="attrs__val">{{ formatVal(v) }}</span>
              </li>
            </ul>
          </dd>
        </div>
        <div v-if="relatedEdges.length">
          <dt>Relations ({{ relatedEdges.length }})</dt>
          <dd>
            <ul class="rels">
              <li v-for="(e, i) in relatedEdges" :key="i">
                <span class="rels__dir">{{ e.direction }}</span>
                <span class="rels__name">{{ e.name }}</span>
                <span class="rels__peer">{{ e.peerName }}</span>
                <p v-if="e.fact" class="rels__fact">{{ e.fact }}</p>
              </li>
            </ul>
          </dd>
        </div>
      </dl>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  graphData: Object,
  loading: Boolean,
})

const query = ref('')
const typeFilter = ref('')
const selected = ref(null)

const PALETTE = ['#ff6a00', '#3ecf8e', '#5ab0ff', '#c983ff', '#ffd166', '#ff5469', '#87d7c3', '#f06292']

const nodes = computed(() => props.graphData?.nodes || [])
const edges = computed(() => props.graphData?.edges || [])
const totalCount = computed(() => nodes.value.length)

const nodeById = computed(() => {
  const m = {}
  nodes.value.forEach(n => { m[n.uuid] = n })
  return m
})

const groups = computed(() => {
  const byType = new Map()
  nodes.value.forEach(n => {
    const type = (n.labels || []).find(l => l !== 'Entity') || 'Entity'
    if (!byType.has(type)) byType.set(type, [])
    byType.get(type).push(n)
  })
  const arr = Array.from(byType.entries()).map(([name, items], i) => ({
    name,
    items,
    color: PALETTE[i % PALETTE.length],
  }))
  arr.sort((a, b) => b.items.length - a.items.length)
  return arr
})

const filteredGroups = computed(() => {
  const q = query.value.trim().toLowerCase()
  return groups.value
    .filter(g => !typeFilter.value || g.name === typeFilter.value)
    .map(g => ({
      ...g,
      items: g.items.filter(n => {
        if (!q) return true
        const hay = [
          n.name,
          (n.labels || []).join(' '),
          n.summary,
        ].filter(Boolean).join(' ').toLowerCase()
        return hay.includes(q)
      }),
    }))
    .filter(g => g.items.length)
})

const relatedEdges = computed(() => {
  if (!selected.value) return []
  const uuid = selected.value.uuid
  return edges.value
    .filter(e => e.source_node_uuid === uuid || e.target_node_uuid === uuid)
    .map(e => {
      const outgoing = e.source_node_uuid === uuid
      const peerId = outgoing ? e.target_node_uuid : e.source_node_uuid
      return {
        direction: outgoing ? '→' : '←',
        name: e.name || '—',
        peerName: nodeById.value[peerId]?.name || peerId,
        fact: e.fact,
      }
    })
})

function select(n) { selected.value = selected.value?.uuid === n.uuid ? null : n }
function formatVal(v) {
  if (v == null) return '—'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}
</script>

<style scoped>
.entities { display: grid; grid-template-columns: 1fr 340px; gap: 14px; min-height: 520px; }
@media (max-width: 1100px) { .entities { grid-template-columns: 1fr; } }

.entities__head {
  grid-column: 1 / -1;
  display: flex; justify-content: space-between; align-items: flex-end;
  gap: 16px; flex-wrap: wrap;
  padding: 14px 16px; border: 1px solid var(--co-border);
  background: var(--co-surface);
}
.entities__eyebrow { font-size: 10px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.entities__head h3 { font-size: 14px; margin-top: 4px; letter-spacing: -0.01em; }
.entities__filters { display: flex; gap: 8px; }
.entities__search, .entities__select {
  background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); padding: 6px 10px; font-size: 12px;
  font-family: var(--co-font-mono);
}
.entities__search { width: 240px; }
.entities__search:focus, .entities__select:focus { outline: none; border-color: var(--co-accent); }

.entities__empty {
  grid-column: 1 / -1;
  padding: 40px; text-align: center; font-size: 13px; color: var(--co-text-dim);
  border: 1px dashed var(--co-border-2); background: var(--co-surface);
}

.entities__groups { display: flex; flex-direction: column; gap: 14px; }

.group { border: 1px solid var(--co-border); background: var(--co-surface); }
.group__head {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-bottom: 1px solid var(--co-border);
}
.group__dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.group__head h4 {
  font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--co-text); flex: 1;
}
.group__count { font-size: 11px; color: var(--co-text-dim); font-family: var(--co-font-mono); }

.cards {
  list-style: none; padding: 8px; margin: 0;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 8px;
}
.card {
  padding: 10px 12px; border: 1px solid var(--co-border);
  background: var(--co-bg); cursor: pointer;
  display: flex; flex-direction: column; gap: 6px;
}
.card:hover { border-color: var(--co-accent); }
.card--on { border-color: var(--co-accent); background: rgba(255,106,0,0.06); }
.card__head { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.card__name { font-size: 13px; color: var(--co-text); font-weight: 500; }
.card__labels { font-size: 10px; color: var(--co-text-dim); font-family: var(--co-font-mono); }
.card__summary { font-size: 11px; color: var(--co-text-dim); line-height: 1.5; margin: 0; }

.drawer {
  border: 1px solid var(--co-border); background: var(--co-surface);
  display: flex; flex-direction: column; overflow: hidden;
  max-height: calc(100vh - 220px); overflow-y: auto;
  position: sticky; top: 16px;
}
.drawer__head {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 14px 16px; border-bottom: 1px solid var(--co-border);
}
.drawer__eyebrow {
  font-size: 10px; letter-spacing: 0.1em; color: var(--co-text-dim);
  font-family: var(--co-font-mono);
}
.drawer__head h3 { font-size: 15px; margin-top: 4px; }
.drawer__close {
  background: transparent; border: none; color: var(--co-text-dim);
  font-size: 22px; cursor: pointer; line-height: 1;
}
.drawer__close:hover { color: var(--co-accent); }

.drawer__fields { padding: 14px 16px; margin: 0; display: flex; flex-direction: column; gap: 14px; }
.drawer__fields dt {
  font-size: 10px; letter-spacing: 0.12em; color: var(--co-text-dim);
  text-transform: uppercase; margin-bottom: 4px;
}
.drawer__fields dd { margin: 0; font-size: 12px; color: var(--co-text); line-height: 1.55; }

.attrs { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.attrs li {
  display: flex; justify-content: space-between; gap: 10px;
  font-size: 11px; font-family: var(--co-font-mono);
  border-bottom: 1px dashed var(--co-border); padding-bottom: 3px;
}
.attrs__key { color: var(--co-text-dim); }
.attrs__val { color: var(--co-text); text-align: right; }

.rels { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.rels li {
  padding: 8px 10px; background: var(--co-bg); border: 1px solid var(--co-border);
}
.rels__dir { color: var(--co-accent); font-family: var(--co-font-mono); margin-right: 6px; }
.rels__name { color: var(--co-text-dim); font-size: 11px; text-transform: lowercase; margin-right: 6px; }
.rels__peer { color: var(--co-text); font-weight: 500; }
.rels__fact { font-size: 11px; color: var(--co-text-dim); line-height: 1.5; margin: 4px 0 0; }
</style>
