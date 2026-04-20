<template>
  <div class="err">
    <div class="err__icon">!</div>
    <h3 class="err__title">{{ title }}</h3>
    <p v-if="body" class="err__body">{{ body }}</p>
    <div class="err__actions">
      <button v-if="retryLabel" class="btn" @click="$emit('retry')">{{ retryLabel }}</button>
      <button v-if="copyable" class="btn btn--ghost" @click="copy">Copy error</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: { type: String, required: true },
  body: String,
  retryLabel: { type: String, default: 'Retry' },
  copyable: { type: Boolean, default: true },
  detail: String,
})
defineEmits(['retry'])
function copy() {
  try { navigator.clipboard?.writeText(props.detail || props.body || props.title) } catch (_) {}
}
</script>

<style scoped>
.err {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; padding: 40px 24px;
  border: 1px solid var(--co-error);
  border-radius: var(--co-radius);
  background: color-mix(in srgb, var(--co-error) 6%, var(--co-surface));
}
.err__icon {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--co-error); color: #000;
  display: grid; place-items: center; font-weight: 700;
  margin-bottom: 12px;
}
.err__title { font-size: 14px; margin-bottom: 6px; color: var(--co-error); }
.err__body { font-size: 13px; color: var(--co-text-dim); max-width: 440px; margin-bottom: 16px; }
.err__actions { display: flex; gap: 8px; }
.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 13px;
  border: 1px solid var(--co-border-2); background: var(--co-surface);
  color: var(--co-text); cursor: pointer; border-radius: var(--co-radius);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--ghost { background: transparent; }
</style>
