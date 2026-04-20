<template>
  <AppModal :model-value="modelValue" :title="title" @update:model-value="cancel">
    <p class="confirm__body">{{ body }}</p>
    <template #footer>
      <button class="btn btn--ghost" @click="cancel">{{ cancelLabel }}</button>
      <button class="btn" :class="`btn--${tone}`" @click="confirm">{{ confirmLabel }}</button>
    </template>
  </AppModal>
</template>

<script setup>
import AppModal from './AppModal.vue'

defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'Confirm' },
  body: { type: String, required: true },
  confirmLabel: { type: String, default: 'Confirm' },
  cancelLabel: { type: String, default: 'Cancel' },
  tone: { type: String, default: 'primary' },
})
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

function confirm() { emit('confirm'); emit('update:modelValue', false) }
function cancel() { emit('cancel'); emit('update:modelValue', false) }
</script>

<style scoped>
.confirm__body { font-size: 13px; color: var(--co-text-dim); line-height: 1.5; }
.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 13px;
  border: 1px solid var(--co-border-2); background: var(--co-surface);
  color: var(--co-text); cursor: pointer; border-radius: var(--co-radius);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); color: #000; border-color: var(--co-accent); }
.btn--primary:hover { background: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
.btn--danger { border-color: var(--co-error); color: var(--co-error); }
.btn--danger:hover { background: var(--co-error); color: #000; }
</style>
