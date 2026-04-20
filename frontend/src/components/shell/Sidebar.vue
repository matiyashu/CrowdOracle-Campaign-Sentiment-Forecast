<template>
  <aside class="sidebar" :class="{ 'sidebar--collapsed': ui.sidebarCollapsed }">
    <div class="sidebar__brand">
      <router-link to="/app" class="brand">
        <span class="brand__mark">▶</span>
        <span v-if="!ui.sidebarCollapsed" class="brand__wordmark">CROWDORACLE</span>
      </router-link>
      <button class="sidebar__toggle" @click="ui.toggleSidebar()" aria-label="Toggle sidebar">
        {{ ui.sidebarCollapsed ? '›' : '‹' }}
      </button>
    </div>

    <SidebarSection label="Workspace" :collapsed="ui.sidebarCollapsed">
      <SidebarItem to="/app/campaigns" label="Campaigns" icon="▣" :badge="campaigns.list.length || undefined" :collapsed="ui.sidebarCollapsed" />
      <SidebarItem to="/app/reality-seeds" label="Reality Seeds" icon="✦" :collapsed="ui.sidebarCollapsed" />
      <SidebarItem to="/app/graph" label="Graph" icon="◈" :collapsed="ui.sidebarCollapsed" />
    </SidebarSection>

    <SidebarSection label="System" :collapsed="ui.sidebarCollapsed">
      <SidebarItem to="/app/settings" label="Settings" icon="⚙" :collapsed="ui.sidebarCollapsed" />
      <SidebarItem to="/app/demo" label="Demo mode" icon="◎" :collapsed="ui.sidebarCollapsed" />
    </SidebarSection>

    <div class="sidebar__foot">
      <DemoModeBadge v-if="demo.active" />
      <div v-if="!ui.sidebarCollapsed" class="sidebar__version">v0.2.0-rc1</div>
    </div>
  </aside>
</template>

<script setup>
import { onMounted } from 'vue'
import SidebarSection from './SidebarSection.vue'
import SidebarItem from './SidebarItem.vue'
import DemoModeBadge from './DemoModeBadge.vue'
import { useUiStore } from '@/stores/ui'
import { useCampaignsStore } from '@/stores/campaigns'
import { useDemoStore } from '@/stores/demo'

const ui = useUiStore()
const campaigns = useCampaignsStore()
const demo = useDemoStore()

onMounted(() => { if (!campaigns.list.length) campaigns.loadList() })
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: var(--co-surface);
  border-right: 1px solid var(--co-border);
  display: flex; flex-direction: column;
  transition: width 0.2s ease;
}
.sidebar--collapsed { width: 56px; }
.sidebar__brand {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--co-border);
}
.brand { display: flex; align-items: center; gap: 8px; color: var(--co-text); }
.brand__mark { color: var(--co-accent); }
.brand__wordmark {
  font-size: 13px; font-weight: 600; letter-spacing: 0.08em;
  border-bottom: 1px solid var(--co-accent);
  padding-bottom: 2px;
}
.sidebar__toggle {
  background: none; border: none; color: var(--co-text-dim);
  cursor: pointer; font-size: 18px; line-height: 1;
}
.sidebar__toggle:hover { color: var(--co-accent); }
.sidebar__foot {
  margin-top: auto;
  padding: 12px 16px;
  border-top: 1px solid var(--co-border);
  display: flex; align-items: center; justify-content: space-between;
}
.sidebar__version { font-size: 10px; color: var(--co-text-mute); }
</style>
