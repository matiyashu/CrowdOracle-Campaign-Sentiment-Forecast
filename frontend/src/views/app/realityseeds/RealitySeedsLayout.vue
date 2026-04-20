<template>
  <section class="rs">
    <header class="rs__head">
      <span class="rs__eyebrow">REALITY SEEDS</span>
      <h1>Simulation workspace</h1>
      <p>Persona-driven agents rehearse your brief on simulated Twitter and Reddit.</p>
    </header>
    <nav class="rs__tabs">
      <router-link :to="{ name: 'SeedsList' }">Seeds</router-link>
      <router-link :to="{ name: 'SeedCreate' }">Upload</router-link>
    </nav>
    <router-view />
  </section>
</template>

<style scoped>
.rs { display: flex; flex-direction: column; gap: 20px; }
.rs__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.rs__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; }
.rs__head p { font-size: 13px; color: var(--co-text-dim); margin-top: 4px; }
.rs__tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--co-border); }
.rs__tabs a {
  padding: 10px 14px; font-size: 13px; color: var(--co-text-dim);
  border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.rs__tabs a:hover { color: var(--co-text); }
.rs__tabs a.router-link-active { color: var(--co-accent); border-color: var(--co-accent); }
</style>
