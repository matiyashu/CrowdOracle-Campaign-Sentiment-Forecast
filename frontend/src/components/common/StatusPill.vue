<template>
  <span class="pill" :class="`pill--${toneFor(status)}`">
    <span class="pill__dot" />
    {{ label || status }}
  </span>
</template>

<script setup>
defineProps({ status: { type: String, required: true }, label: String })
function toneFor(s) {
  const m = {
    active: 'success', running: 'success', completed: 'success',
    draft: 'neutral', idle: 'neutral',
    archived: 'muted', inactive: 'muted',
    failed: 'error', error: 'error',
    warning: 'warn', partial: 'warn',
  }
  return m[(s || '').toLowerCase()] || 'neutral'
}
</script>

<style scoped>
.pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 10px;
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border-radius: 999px;
  border: 1px solid var(--co-border-2);
  background: var(--co-surface-2);
  color: var(--co-text-dim);
}
.pill__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.pill--success { color: var(--co-success); border-color: var(--co-success); }
.pill--warn { color: var(--co-warn); border-color: var(--co-warn); }
.pill--error { color: var(--co-error); border-color: var(--co-error); }
.pill--muted { opacity: 0.6; }
</style>
