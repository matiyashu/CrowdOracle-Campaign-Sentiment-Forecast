<template>
  <Teleport to="body">
    <div class="toasts">
      <TransitionGroup name="toast">
        <div
          v-for="t in ui.toasts"
          :key="t.id"
          :class="['toast', `toast--${t.tone}`]"
          @click="ui.dismissToast(t.id)"
        >
          <div class="toast__body">
            <div v-if="t.title" class="toast__title">{{ t.title }}</div>
            <div v-if="t.body" class="toast__text">{{ t.body }}</div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<style scoped>
.toasts {
  position: fixed; bottom: 20px; right: 20px;
  display: flex; flex-direction: column; gap: 8px;
  z-index: 1100;
}
.toast {
  min-width: 280px; max-width: 400px;
  padding: 12px 14px;
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  border-left-width: 3px;
  cursor: pointer;
  box-shadow: var(--co-shadow);
}
.toast--success { border-left-color: var(--co-success); }
.toast--error   { border-left-color: var(--co-error); }
.toast--warn    { border-left-color: var(--co-warn); }
.toast--info    { border-left-color: var(--co-accent); }
.toast__title { font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.toast__text { font-size: 13px; color: var(--co-text-dim); margin-top: 4px; }
.toast-enter-active, .toast-leave-active { transition: all 0.2s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(20px); }
</style>
