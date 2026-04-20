<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="['btn', `btn--${variant}`, { 'btn--block': block, 'btn--loading': loading }]"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner" />
    <slot v-else />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'primary' },
  type: { type: String, default: 'button' },
  disabled: Boolean,
  loading: Boolean,
  block: Boolean,
})
defineEmits(['click'])
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  font-family: var(--co-font-mono);
  font-size: 13px;
  font-weight: 500;
  border: 1px solid var(--co-border-2);
  border-radius: var(--co-radius);
  background: var(--co-surface);
  color: var(--co-text);
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}
.btn:hover:not(:disabled) { border-color: var(--co-accent); color: var(--co-accent); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn--primary {
  background: var(--co-accent);
  border-color: var(--co-accent);
  color: #000;
}
.btn--primary:hover:not(:disabled) {
  background: var(--co-accent-2);
  border-color: var(--co-accent-2);
  color: #000;
}
.btn--ghost { background: transparent; }
.btn--danger { border-color: var(--co-error); color: var(--co-error); }
.btn--danger:hover:not(:disabled) { background: var(--co-error); color: #000; }
.btn--block { width: 100%; }
.spinner {
  width: 12px; height: 12px; border-radius: 50%;
  border: 2px solid currentColor; border-top-color: transparent;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
