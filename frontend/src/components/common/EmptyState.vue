<template>
  <div class="empty">
    <div v-if="icon" class="empty__icon">{{ icon }}</div>
    <h3 class="empty__title">{{ title }}</h3>
    <p v-if="body" class="empty__body">{{ body }}</p>
    <div class="empty__actions">
      <slot>
        <button v-if="primary" class="btn btn--primary" @click="$emit('primary')">{{ primary }}</button>
        <button v-if="secondary" class="btn btn--ghost" @click="$emit('secondary')">{{ secondary }}</button>
      </slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '◇' },
  title: { type: String, required: true },
  body: String,
  primary: String,
  secondary: String,
})
defineEmits(['primary', 'secondary'])
</script>

<style scoped>
.empty {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; padding: 48px 24px;
  border: 1px dashed var(--co-border-2);
  border-radius: var(--co-radius);
  background: var(--co-surface);
}
.empty__icon { font-size: 28px; color: var(--co-accent); margin-bottom: 12px; }
.empty__title { font-size: 15px; margin-bottom: 6px; color: var(--co-text); }
.empty__body { font-size: 13px; color: var(--co-text-dim); max-width: 440px; margin-bottom: 16px; }
.empty__actions { display: flex; gap: 8px; }
.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 13px;
  border: 1px solid var(--co-border-2); background: var(--co-surface);
  color: var(--co-text); cursor: pointer; border-radius: var(--co-radius);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); color: #000; border-color: var(--co-accent); }
.btn--primary:hover { background: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
