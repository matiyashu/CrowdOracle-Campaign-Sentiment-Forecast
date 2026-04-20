<template>
  <span class="badge" :class="`badge--${tone}`"><slot /></span>
</template>

<script setup>
defineProps({ tone: { type: String, default: 'neutral' } })
</script>

<style scoped>
.badge {
  display: inline-flex; align-items: center;
  padding: 2px 8px;
  font-size: 10px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-radius: 999px;
  border: 1px solid var(--co-border-2);
  background: var(--co-surface-2);
  color: var(--co-text-dim);
}
.badge--accent { border-color: var(--co-accent); color: var(--co-accent); background: transparent; }
.badge--success { border-color: var(--co-success); color: var(--co-success); }
.badge--warn { border-color: var(--co-warn); color: var(--co-warn); }
.badge--error { border-color: var(--co-error); color: var(--co-error); }
</style>
