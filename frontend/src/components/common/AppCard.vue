<template>
  <section class="card" :class="{ 'card--hover': hover }">
    <header v-if="title || $slots.header" class="card__header">
      <slot name="header">
        <h3 class="card__title">{{ title }}</h3>
      </slot>
      <div v-if="$slots.actions" class="card__actions"><slot name="actions" /></div>
    </header>
    <div class="card__body"><slot /></div>
    <footer v-if="$slots.footer" class="card__footer"><slot name="footer" /></footer>
  </section>
</template>

<script setup>
defineProps({ title: String, hover: Boolean })
</script>

<style scoped>
.card {
  background: var(--co-surface);
  border: 1px solid var(--co-border);
  border-radius: var(--co-radius);
  display: flex; flex-direction: column;
}
.card--hover:hover { border-color: var(--co-accent); }
.card__header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--co-border);
}
.card__title { font-size: 12px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: var(--co-text-dim); }
.card__actions { display: flex; gap: 8px; }
.card__body { padding: 18px; }
.card__footer { padding: 12px 18px; border-top: 1px solid var(--co-border); font-size: 12px; color: var(--co-text-dim); }
</style>
