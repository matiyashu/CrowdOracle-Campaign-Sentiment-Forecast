<template>
  <section class="page">
    <header class="page__head">
      <div>
        <span class="page__eyebrow">WORKSPACE</span>
        <h1>Campaigns</h1>
      </div>
      <router-link to="/app/campaigns/new" class="btn btn--primary">+ New campaign</router-link>
    </header>

    <EmptyState title="No campaigns yet." body="Start from a demo package or build one from your brief.">
      <router-link to="/app/demo" class="btn btn--primary">Try a demo campaign</router-link>
      <router-link to="/app/campaigns/new" class="btn btn--ghost">+ New campaign</router-link>
    </EmptyState>
  </section>
</template>

<script setup>
import EmptyState from '@/components/common/EmptyState.vue'
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 24px; }
.page__head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.page__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.page__head h1 { font-size: 24px; margin-top: 6px; letter-spacing: -0.01em; }
.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
