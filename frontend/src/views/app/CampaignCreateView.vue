<template>
  <section class="page">
    <header class="page__head">
      <span class="page__eyebrow">WORKSPACE / NEW</span>
      <h1>Create a campaign</h1>
      <p>Three steps: basics, channels, and initial uploads.</p>
    </header>
    <div class="page__stub">Campaign creation wizard ships in Sprint B.</div>
  </section>
</template>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; max-width: 720px; }
.page__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.page__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; }
.page__head p { font-size: 14px; color: var(--co-text-dim); }
.page__stub {
  padding: 32px; background: var(--co-surface);
  border: 1px dashed var(--co-border-2); color: var(--co-text-dim);
  font-size: 13px; text-align: center;
}
</style>
