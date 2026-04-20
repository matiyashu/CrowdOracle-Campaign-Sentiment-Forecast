<template>
  <header class="topbar">
    <Breadcrumbs />
    <button class="topbar__search" @click="ui.openCommandPalette()">
      <span class="topbar__search-icon">⌘</span>
      <span class="topbar__search-text">Search campaigns, creatives, settings…</span>
      <span class="topbar__search-kbd">{{ isMac ? '⌘K' : 'Ctrl K' }}</span>
    </button>
    <div class="topbar__right">
      <span v-if="demo.active" class="topbar__demo">DEMO · <button @click="exitDemo">Exit</button></span>
      <UserMenu />
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Breadcrumbs from './Breadcrumbs.vue'
import UserMenu from './UserMenu.vue'
import { useUiStore } from '@/stores/ui'
import { useDemoStore } from '@/stores/demo'

const ui = useUiStore()
const demo = useDemoStore()
const router = useRouter()

const isMac = computed(() =>
  typeof navigator !== 'undefined' && /Mac/i.test(navigator.platform || '')
)

async function exitDemo() {
  await demo.reset()
  router.push('/app/campaigns')
}
</script>

<style scoped>
.topbar {
  display: flex; align-items: center; gap: 16px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--co-border);
  background: var(--co-bg);
  height: 48px;
}
.topbar__search {
  flex: 1; max-width: 480px;
  display: flex; align-items: center; gap: 10px;
  padding: 6px 12px;
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  border-radius: var(--co-radius);
  color: var(--co-text-dim);
  cursor: pointer;
  font-family: var(--co-font-mono);
  font-size: 12px;
}
.topbar__search:hover { border-color: var(--co-accent); color: var(--co-text); }
.topbar__search-icon { color: var(--co-text-mute); }
.topbar__search-text { flex: 1; text-align: left; }
.topbar__search-kbd {
  font-size: 10px; padding: 2px 6px;
  border: 1px solid var(--co-border-2);
  border-radius: var(--co-radius);
  color: var(--co-text-mute);
}
.topbar__right { display: flex; align-items: center; gap: 12px; margin-left: auto; }
.topbar__demo {
  font-size: 10px; letter-spacing: 0.08em;
  color: var(--co-accent);
  border: 1px solid var(--co-accent);
  padding: 2px 8px;
  border-radius: 999px;
}
.topbar__demo button {
  background: none; border: none; color: inherit;
  text-decoration: underline; cursor: pointer;
  font-family: inherit; font-size: inherit;
}
</style>
