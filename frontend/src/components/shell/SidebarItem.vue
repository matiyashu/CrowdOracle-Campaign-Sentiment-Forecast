<template>
  <router-link :to="to" class="item" active-class="item--active" :class="{ 'item--collapsed': collapsed }">
    <span class="item__icon">{{ icon || '›' }}</span>
    <span v-if="!collapsed" class="item__label">{{ label }}</span>
    <span v-if="!collapsed && badge != null" class="item__badge">{{ badge }}</span>
  </router-link>
</template>

<script setup>
defineProps({
  to: { type: [String, Object], required: true },
  label: { type: String, required: true },
  icon: String,
  badge: [Number, String],
  collapsed: Boolean,
})
</script>

<style scoped>
.item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 16px;
  color: var(--co-text-dim);
  font-size: 13px;
  border-left: 2px solid transparent;
  transition: color 0.15s, background 0.15s, border-color 0.15s;
}
.item:hover { color: var(--co-text); background: rgba(255,255,255,0.03); }
.item--active {
  color: var(--co-accent);
  background: rgba(255,106,0,0.08);
  border-left-color: var(--co-accent);
}
.item__icon { width: 16px; text-align: center; opacity: 0.7; }
.item__label { flex: 1; }
.item__badge {
  font-size: 10px;
  padding: 1px 6px;
  background: var(--co-border-2);
  border-radius: 999px;
  color: var(--co-text-dim);
}
.item--collapsed { justify-content: center; padding: 10px 0; }
</style>
