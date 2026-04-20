<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="modelValue" class="drawer" @click.self="close">
        <aside class="drawer__panel" :class="`drawer__panel--${side}`">
          <header v-if="title || $slots.header" class="drawer__header">
            <slot name="header"><h3>{{ title }}</h3></slot>
            <button class="drawer__close" @click="close" aria-label="Close">×</button>
          </header>
          <div class="drawer__body"><slot /></div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  title: String,
  side: { type: String, default: 'right' },
})
const emit = defineEmits(['update:modelValue'])
function close() { emit('update:modelValue', false) }
</script>

<style scoped>
.drawer {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 900;
}
.drawer__panel {
  position: absolute; top: 0; bottom: 0;
  width: min(480px, 100%);
  background: var(--co-surface);
  border-left: 1px solid var(--co-border-2);
  display: flex; flex-direction: column;
}
.drawer__panel--right { right: 0; }
.drawer__panel--left { left: 0; border-left: none; border-right: 1px solid var(--co-border-2); }
.drawer__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--co-border);
}
.drawer__header h3 { font-size: 14px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }
.drawer__close { background: none; border: none; color: var(--co-text-dim); font-size: 22px; cursor: pointer; line-height: 1; }
.drawer__close:hover { color: var(--co-accent); }
.drawer__body { flex: 1; padding: 20px; overflow-y: auto; }
.drawer-enter-active, .drawer-leave-active { transition: opacity 0.2s; }
.drawer-enter-active .drawer__panel, .drawer-leave-active .drawer__panel { transition: transform 0.2s ease; }
.drawer-enter-from, .drawer-leave-to { opacity: 0; }
.drawer-enter-from .drawer__panel--right, .drawer-leave-to .drawer__panel--right { transform: translateX(100%); }
.drawer-enter-from .drawer__panel--left, .drawer-leave-to .drawer__panel--left { transform: translateX(-100%); }
</style>
