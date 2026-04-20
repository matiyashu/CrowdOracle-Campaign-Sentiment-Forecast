<template>
  <div class="wb">
    <div class="wb__graph">
      <GraphPanel
        :graph-data="graphData"
        :loading="loading"
        :current-phase="currentPhase"
        :is-simulating="isSimulating"
        @refresh="$emit('refresh')"
        @toggle-maximize="$emit('toggle-maximize')"
      />
    </div>

    <section class="wb__console">
      <header class="wb__head">
        <div class="wb__tabs">
          <button
            v-for="t in tabs"
            :key="t.value"
            class="wb__tab"
            :class="{ 'wb__tab--on': activeTab === t.value }"
            @click="activeTab = t.value"
          >{{ t.label }}
            <span v-if="t.count" class="wb__count">{{ t.count }}</span>
          </button>
        </div>
      </header>

      <div class="wb__body">
        <div v-if="activeTab === 'actions'">
          <div v-if="!actions?.length" class="wb__empty">No agent actions yet. Start a run to see activity.</div>
          <ul v-else class="actions">
            <li v-for="(a, i) in actions.slice(0, 80)" :key="a.id || i" class="actions__row">
              <span class="actions__round">r{{ a.round_num ?? '?' }}</span>
              <span class="actions__agent">{{ a.agent_name || `agent ${a.agent_id}` }}</span>
              <span class="actions__kind">{{ a.action_type || a.action || '—' }}</span>
              <span v-if="a.content" class="actions__content">{{ trim(a.content, 140) }}</span>
            </li>
          </ul>
        </div>

        <div v-else-if="activeTab === 'chat'">
          <div v-if="!messages?.length" class="wb__empty">Chat with the report agent appears here.</div>
          <ul v-else class="chat">
            <li
              v-for="(m, i) in messages"
              :key="i"
              class="chat__row"
              :class="'chat__row--' + (m.role || 'user')"
            >
              <span class="chat__role">{{ (m.role || 'user').toUpperCase() }}</span>
              <span class="chat__text">{{ m.content }}</span>
            </li>
          </ul>
          <form class="chat__form" @submit.prevent="send">
            <input v-model="draft" placeholder="Ask about this simulation…" />
            <button type="submit" :disabled="!draft || sending">{{ sending ? '…' : 'Send' }}</button>
          </form>
        </div>

        <div v-else-if="activeTab === 'log'">
          <pre v-if="log" class="log">{{ log }}</pre>
          <div v-else class="wb__empty">No log output yet.</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import GraphPanel from './GraphPanel.vue'

const props = defineProps({
  graphData: Object,
  loading: Boolean,
  currentPhase: Number,
  isSimulating: Boolean,
  actions: { type: Array, default: () => [] },
  messages: { type: Array, default: () => [] },
  log: { type: String, default: '' },
  sending: Boolean,
})

const emit = defineEmits(['refresh', 'toggle-maximize', 'send-message'])

const activeTab = ref('actions')
const draft = ref('')

const tabs = computed(() => [
  { value: 'actions', label: 'Actions', count: props.actions?.length || 0 },
  { value: 'chat',    label: 'Chat',    count: props.messages?.length || 0 },
  { value: 'log',     label: 'Log',     count: 0 },
])

function trim(s, n) { return s.length > n ? s.slice(0, n) + '…' : s }
function send() {
  if (!draft.value) return
  emit('send-message', draft.value)
  draft.value = ''
}
</script>

<style scoped>
.wb { display: grid; grid-template-rows: minmax(360px, 1fr) 300px; gap: 14px; height: 100%; min-height: 640px; }

.wb__graph {
  background: var(--co-surface); border: 1px solid var(--co-border);
  overflow: hidden; min-height: 360px;
}

.wb__console {
  background: var(--co-surface); border: 1px solid var(--co-border);
  display: flex; flex-direction: column; overflow: hidden;
}
.wb__head { border-bottom: 1px solid var(--co-border); }
.wb__tabs { display: flex; gap: 0; }
.wb__tab {
  padding: 10px 16px; background: transparent; border: none; cursor: pointer;
  color: var(--co-text-dim); font-family: var(--co-font-mono); font-size: 12px;
  border-bottom: 2px solid transparent; margin-bottom: -1px;
  display: flex; align-items: center; gap: 6px;
}
.wb__tab:hover { color: var(--co-text); }
.wb__tab--on { color: var(--co-accent); border-color: var(--co-accent); }
.wb__count {
  font-size: 10px; background: var(--co-bg);
  border: 1px solid var(--co-border-2); padding: 1px 6px;
}

.wb__body { flex: 1; overflow: auto; padding: 12px 14px; }
.wb__empty { font-size: 12px; color: var(--co-text-mute, #666); padding: 18px; text-align: center; }

.actions { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; font-size: 11px; }
.actions__row {
  display: grid; grid-template-columns: 40px 140px 80px 1fr; gap: 10px;
  padding: 4px 0; border-bottom: 1px dashed var(--co-border);
}
.actions__round { color: var(--co-text-dim); font-family: var(--co-font-mono); }
.actions__agent { color: var(--co-text); }
.actions__kind {
  font-size: 10px; color: var(--co-accent); text-transform: uppercase;
  letter-spacing: 0.05em;
}
.actions__content { color: var(--co-text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.chat { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.chat__row { display: flex; gap: 8px; font-size: 12px; }
.chat__role {
  font-size: 9px; letter-spacing: 0.12em; padding: 2px 6px;
  border: 1px solid var(--co-border-2); color: var(--co-text-dim);
  min-width: 54px; text-align: center;
}
.chat__row--assistant .chat__role { color: var(--co-accent); border-color: var(--co-accent); }
.chat__text { color: var(--co-text); line-height: 1.5; }

.chat__form {
  display: flex; gap: 6px; padding: 10px 0 0; margin-top: 10px;
  border-top: 1px solid var(--co-border);
}
.chat__form input {
  flex: 1; background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); padding: 6px 10px; font-size: 12px;
  font-family: var(--co-font-mono);
}
.chat__form input:focus { outline: none; border-color: var(--co-accent); }
.chat__form button {
  padding: 6px 14px; background: var(--co-accent); border: 1px solid var(--co-accent);
  color: #000; cursor: pointer; font-family: var(--co-font-mono); font-size: 12px;
}
.chat__form button:disabled { opacity: 0.5; cursor: not-allowed; }

.log {
  font-family: var(--co-font-mono); font-size: 11px; line-height: 1.5;
  color: var(--co-text); white-space: pre-wrap; margin: 0;
  background: var(--co-bg); padding: 10px; border: 1px solid var(--co-border);
  max-height: 100%; overflow: auto;
}
</style>
