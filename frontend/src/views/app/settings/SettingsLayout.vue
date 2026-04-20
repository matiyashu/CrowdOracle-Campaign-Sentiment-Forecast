<template>
  <section class="settings">
    <aside class="settings__nav">
      <span class="settings__eyebrow">SETTINGS</span>
      <router-link :to="{ name: 'SettingsProviders' }">Providers</router-link>
      <router-link :to="{ name: 'SettingsRouting' }">Task routing</router-link>
      <router-link :to="{ name: 'SettingsWorkspace' }">Workspace</router-link>
      <router-link :to="{ name: 'SettingsApiKeys' }">API keys</router-link>
    </aside>
    <div class="settings__main">
      <router-view />
    </div>
  </section>
</template>

<style scoped>
.settings {
  display: grid; grid-template-columns: 200px 1fr;
  gap: 32px; align-items: flex-start;
}
.settings__nav { display: flex; flex-direction: column; gap: 2px; position: sticky; top: 72px; }
.settings__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); margin-bottom: 10px; }
.settings__nav a {
  padding: 8px 10px; font-size: 13px; color: var(--co-text-dim);
  border-left: 2px solid transparent;
}
.settings__nav a:hover { color: var(--co-accent); }
.settings__nav a.router-link-active {
  color: var(--co-text); border-color: var(--co-accent); background: var(--co-surface);
}

@media (max-width: 760px) {
  .settings { grid-template-columns: 1fr; }
  .settings__nav { position: static; flex-direction: row; flex-wrap: wrap; }
}
</style>
