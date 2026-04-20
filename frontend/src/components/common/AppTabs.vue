<template>
  <nav class="tabs" role="tablist">
    <router-link
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="tabs__item"
      active-class="tabs__item--active"
    >
      {{ tab.label }}
      <span v-if="tab.badge != null" class="tabs__badge">{{ tab.badge }}</span>
    </router-link>
  </nav>
</template>

<script setup>
defineProps({
  tabs: { type: Array, required: true },
})
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--co-border);
}
.tabs__item {
  padding: 10px 14px;
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--co-text-dim);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  display: inline-flex; align-items: center; gap: 8px;
}
.tabs__item:hover { color: var(--co-text); }
.tabs__item--active {
  color: var(--co-accent);
  border-bottom-color: var(--co-accent);
}
.tabs__badge {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--co-border-2);
  color: var(--co-text);
  border-radius: 999px;
}
</style>
