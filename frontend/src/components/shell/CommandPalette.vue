<template>
  <Teleport to="body">
    <Transition name="cp">
      <div v-if="ui.commandPaletteOpen" class="cp" @click.self="ui.closeCommandPalette()">
        <div class="cp__panel">
          <input
            ref="inputEl"
            v-model="query"
            class="cp__input"
            placeholder="Search campaigns, settings, commands…"
            @keydown.down.prevent="move(1)"
            @keydown.up.prevent="move(-1)"
            @keydown.enter.prevent="run()"
            @keydown.esc.prevent="ui.closeCommandPalette()"
          />
          <ul class="cp__list">
            <li
              v-for="(r, i) in results"
              :key="`${r.kind}-${r.to}-${i}`"
              :class="['cp__item', { 'cp__item--active': i === cursor }]"
              @click="exec(r)"
              @mouseenter="cursor = i"
            >
              <span class="cp__kind">{{ r.kind }}</span>
              <span class="cp__label">{{ r.label }}</span>
              <span v-if="r.sub" class="cp__sub">{{ r.sub }}</span>
            </li>
            <li v-if="!results.length" class="cp__empty">No matches.</li>
          </ul>
          <div class="cp__foot">
            <span>↑↓ navigate</span><span>⏎ open</span><span>esc close</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useCommandPalette } from '@/composables/useCommandPalette'

const ui = useUiStore()
const { sources, execute } = useCommandPalette()

const query = ref('')
const cursor = ref(0)
const inputEl = ref(null)

const results = computed(() => {
  const q = query.value.trim().toLowerCase()
  const all = sources()
  if (!q) return all.slice(0, 12)
  return all
    .filter((s) => (s.label + ' ' + (s.sub || '')).toLowerCase().includes(q))
    .slice(0, 20)
})

watch(() => ui.commandPaletteOpen, async (open) => {
  if (open) {
    query.value = ''
    cursor.value = 0
    await nextTick()
    inputEl.value?.focus()
  }
})

function move(d) {
  const n = results.value.length
  if (!n) return
  cursor.value = (cursor.value + d + n) % n
}
function run() { const r = results.value[cursor.value]; if (r) exec(r) }
function exec(r) { execute(r) }
</script>

<style scoped>
.cp {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex; align-items: flex-start; justify-content: center;
  padding-top: 12vh;
  z-index: 1200;
}
.cp__panel {
  width: min(640px, 92%);
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  box-shadow: var(--co-shadow);
}
.cp__input {
  width: 100%;
  padding: 16px 20px;
  font-family: var(--co-font-mono);
  font-size: 15px;
  color: var(--co-text);
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--co-border);
  outline: none;
}
.cp__input::placeholder { color: var(--co-text-mute); }
.cp__list { list-style: none; max-height: 320px; overflow-y: auto; }
.cp__item {
  display: flex; align-items: baseline; gap: 12px;
  padding: 10px 20px;
  cursor: pointer;
  border-left: 2px solid transparent;
}
.cp__item--active { background: rgba(255,106,0,0.06); border-left-color: var(--co-accent); }
.cp__kind {
  font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--co-text-mute); min-width: 60px;
}
.cp__label { flex: 1; font-size: 13px; color: var(--co-text); }
.cp__sub { font-size: 11px; color: var(--co-text-dim); }
.cp__empty { padding: 20px; text-align: center; color: var(--co-text-mute); font-size: 13px; }
.cp__foot {
  display: flex; gap: 16px;
  padding: 8px 20px;
  border-top: 1px solid var(--co-border);
  font-size: 10px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--co-text-mute);
}
.cp-enter-active, .cp-leave-active { transition: opacity 0.15s; }
.cp-enter-from, .cp-leave-to { opacity: 0; }
</style>
