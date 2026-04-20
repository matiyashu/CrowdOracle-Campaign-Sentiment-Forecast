<template>
  <div class="split">
    <div class="split__graph">
      <GraphPanel
        :graph-data="graphData"
        :loading="loading"
        :current-phase="currentPhase"
        :is-simulating="isSimulating"
        @refresh="$emit('refresh')"
        @toggle-maximize="$emit('toggle-maximize')"
      />
    </div>

    <aside class="split__docs">
      <header class="split__head">
        <h3>Source documents</h3>
        <span v-if="documents?.length" class="split__count">{{ documents.length }}</span>
      </header>

      <div v-if="!documents?.length" class="split__empty">
        No source documents attached to this seed yet.
      </div>

      <ul v-else class="docs">
        <li
          v-for="d in documents"
          :key="d.id || d.filename"
          class="docs__row"
          :class="{ 'docs__row--on': activeDoc?.id === d.id }"
          @click="selectDoc(d)"
        >
          <span class="docs__name">{{ d.filename || d.name || '—' }}</span>
          <span class="docs__type">{{ d.file_type || d.kind || '' }}</span>
        </li>
      </ul>

      <div v-if="activeDoc?.content" class="docs__content">
        <pre>{{ activeDoc.content }}</pre>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import GraphPanel from './GraphPanel.vue'

defineProps({
  graphData: Object,
  loading: Boolean,
  currentPhase: Number,
  isSimulating: Boolean,
  documents: { type: Array, default: () => [] },
})

defineEmits(['refresh', 'toggle-maximize'])

const activeDoc = ref(null)
function selectDoc(d) { activeDoc.value = activeDoc.value?.id === d.id ? null : d }
</script>

<style scoped>
.split { display: grid; grid-template-columns: 1fr 380px; gap: 14px; height: 100%; min-height: 520px; }
@media (max-width: 1100px) { .split { grid-template-columns: 1fr; } }

.split__graph {
  background: var(--co-surface); border: 1px solid var(--co-border);
  min-height: 520px; overflow: hidden;
}

.split__docs {
  background: var(--co-surface); border: 1px solid var(--co-border);
  display: flex; flex-direction: column; gap: 0;
  max-height: calc(100vh - 260px); overflow: hidden;
}
.split__head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 14px; border-bottom: 1px solid var(--co-border);
}
.split__head h3 { font-size: 11px; letter-spacing: 0.1em; color: var(--co-text-dim); text-transform: uppercase; }
.split__count { font-size: 11px; color: var(--co-text-dim); }
.split__empty { padding: 20px; font-size: 12px; color: var(--co-text-mute, #666); text-align: center; }

.docs { list-style: none; padding: 0; margin: 0; overflow-y: auto; }
.docs__row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px; border-bottom: 1px solid var(--co-border);
  cursor: pointer; font-size: 12px;
}
.docs__row:hover { background: var(--co-bg); }
.docs__row--on { background: var(--co-bg); color: var(--co-accent); }
.docs__name { color: var(--co-text); font-family: var(--co-font-mono); }
.docs__type { font-size: 10px; color: var(--co-text-dim); text-transform: uppercase; }

.docs__content {
  border-top: 1px solid var(--co-border);
  background: var(--co-bg); flex: 1; overflow: auto;
  max-height: 260px;
}
.docs__content pre {
  font-size: 11px; line-height: 1.5; padding: 12px;
  color: var(--co-text); white-space: pre-wrap; margin: 0;
}
</style>
