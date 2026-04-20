<template>
  <div class="nf">
    <span class="nf__code">404</span>
    <h1>This page didn't make the forecast.</h1>
    <p>The URL you opened doesn't match any known route.</p>
    <div class="nf__cta">
      <router-link to="/app/campaigns" class="btn btn--primary">Go to campaigns</router-link>
      <router-link to="/" class="btn btn--ghost">Home</router-link>
    </div>
  </div>
</template>

<style scoped>
.nf {
  min-height: calc(100vh - 64px);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 40px 24px;
  color: var(--co-text);
}
.nf__code {
  font-family: var(--co-font-mono); font-size: 13px;
  letter-spacing: 0.15em; color: var(--co-accent);
}
.nf h1 { font-size: clamp(24px, 3vw, 34px); margin: 16px 0 8px; letter-spacing: -0.02em; }
.nf p { color: var(--co-text-dim); margin-bottom: 28px; }
.nf__cta { display: inline-flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.btn {
  padding: 10px 18px; font-family: var(--co-font-mono); font-size: 12px;
  border-radius: var(--co-radius);
  border: 1px solid var(--co-border-2);
  background: var(--co-surface);
  color: var(--co-text);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
