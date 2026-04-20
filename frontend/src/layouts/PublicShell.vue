<template>
  <div class="public">
    <header class="public__nav">
      <router-link to="/" class="public__brand">
        <span class="public__mark">▶</span>
        <span class="public__word">CROWDORACLE</span>
      </router-link>
      <nav class="public__links">
        <router-link to="/product">Product</router-link>
        <router-link to="/pricing">Pricing</router-link>
        <router-link to="/docs">Docs</router-link>
      </nav>
      <div class="public__cta">
        <router-link to="/login" class="btn btn--ghost">Sign in</router-link>
        <router-link to="/app/demo" class="btn btn--primary">Start free</router-link>
      </div>
    </header>
    <main class="public__main">
      <router-view />
    </main>
    <ToastStack />
  </div>
</template>

<script setup>
import ToastStack from '@/components/common/ToastStack.vue'
</script>

<style scoped>
.public {
  min-height: 100vh;
  display: flex; flex-direction: column;
  background: var(--co-bg);
}
.public__nav {
  display: flex; align-items: center;
  padding: 16px 32px;
  border-bottom: 1px solid var(--co-border);
  gap: 40px;
  height: 64px;
}
.public__brand { display: flex; align-items: center; gap: 8px; }
.public__mark { color: var(--co-accent); }
.public__word {
  font-size: 13px; font-weight: 600; letter-spacing: 0.08em;
  border-bottom: 1px solid var(--co-accent);
  padding-bottom: 2px;
}
.public__links {
  display: flex; gap: 24px;
  flex: 1; justify-content: center;
}
.public__links a {
  font-size: 13px; color: var(--co-text-dim);
}
.public__links a:hover { color: var(--co-accent); }
.public__links a.router-link-active { color: var(--co-text); }
.public__cta { display: flex; gap: 8px; }
.btn {
  padding: 8px 16px;
  font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2);
  background: var(--co-surface);
  color: var(--co-text);
  border-radius: var(--co-radius);
  cursor: pointer;
  letter-spacing: 0.02em;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--ghost { background: transparent; border-color: transparent; }
.btn--ghost:hover { background: var(--co-surface); }
.btn--primary { background: var(--co-accent); color: #000; border-color: var(--co-accent); }
.btn--primary:hover { background: var(--co-accent-2); color: #000; border-color: var(--co-accent-2); }
.public__main { flex: 1; }

@media (max-width: 720px) {
  .public__nav { padding: 12px 16px; gap: 12px; }
  .public__links { display: none; }
}
</style>
