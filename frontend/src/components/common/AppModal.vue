<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal" @click.self="close">
        <div class="modal__panel" role="dialog" aria-modal="true">
          <header v-if="title || $slots.header" class="modal__header">
            <slot name="header"><h3>{{ title }}</h3></slot>
            <button class="modal__close" @click="close" aria-label="Close">×</button>
          </header>
          <div class="modal__body"><slot /></div>
          <footer v-if="$slots.footer" class="modal__footer"><slot name="footer" /></footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const props = defineProps({ modelValue: Boolean, title: String })
const emit = defineEmits(['update:modelValue', 'close'])
function close() { emit('update:modelValue', false); emit('close') }
</script>

<style scoped>
.modal {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 24px;
}
.modal__panel {
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  box-shadow: var(--co-shadow);
  width: min(560px, 100%);
  max-height: 90vh;
  display: flex; flex-direction: column;
}
.modal__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--co-border);
}
.modal__header h3 { font-size: 14px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }
.modal__close {
  background: none; border: none; color: var(--co-text-dim);
  font-size: 22px; cursor: pointer; line-height: 1;
}
.modal__close:hover { color: var(--co-accent); }
.modal__body { padding: 20px; overflow-y: auto; }
.modal__footer {
  padding: 14px 20px;
  border-top: 1px solid var(--co-border);
  display: flex; justify-content: flex-end; gap: 8px;
}
.modal-enter-active, .modal-leave-active { transition: opacity 0.15s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
