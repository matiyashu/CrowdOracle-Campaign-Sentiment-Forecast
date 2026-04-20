<template>
  <div class="docs">
    <aside class="docs__nav">
      <span class="docs__eyebrow">DOCS</span>
      <nav>
        <a href="#getting-started">Getting started</a>
        <a href="#campaigns">Campaigns</a>
        <a href="#creatives">Creative intelligence</a>
        <a href="#reality-seeds">Reality Seeds</a>
        <a href="#providers">AI providers</a>
        <a href="#api">API reference</a>
      </nav>
    </aside>

    <article class="docs__body">
      <section id="getting-started">
        <h1>Getting started</h1>
        <p>Load a demo campaign to see every surface populated, then create your first workspace when you're ready to bring real data in.</p>
        <ol>
          <li>Open <router-link to="/app/demo">the demo launcher</router-link> and pick a package.</li>
          <li>Inspect the Overview tab — this is the canonical executive view.</li>
          <li>Walk through Creatives → Mentions → Sentiment → Impact → Report.</li>
          <li>Configure your own AI provider in Settings → Providers before importing real data.</li>
        </ol>
      </section>

      <section id="campaigns">
        <h2>Campaigns</h2>
        <p>A campaign is a named container for everything related to one marketing push — brief, creatives, mentions, performance, and the generated report.</p>
      </section>

      <section id="creatives">
        <h2>Creative intelligence</h2>
        <p>Upload images, video, or copy. We run OCR, transcription, hook/CTA extraction, and downstream attribution per asset.</p>
      </section>

      <section id="reality-seeds">
        <h2>Reality Seeds</h2>
        <p>Reality Seeds rehearses a campaign on a simulated Twitter and Reddit using persona agents. Use it to pressure-test a brief before it goes live.</p>
      </section>

      <section id="providers">
        <h2>AI providers</h2>
        <p>Bring your own OpenAI, Anthropic, Qwen, Gemini, or OpenAI-compatible endpoint. Route per task in Settings → Routing.</p>
      </section>

      <section id="api">
        <h2>API reference</h2>
        <p>Full OpenAPI surface forthcoming. All endpoints live under <code>/api/*</code>.</p>
      </section>
    </article>
  </div>
</template>

<style scoped>
.docs {
  display: grid; grid-template-columns: 220px 1fr;
  gap: 40px; max-width: 1100px; margin: 0 auto;
  padding: 60px 32px 80px;
  color: var(--co-text);
}
.docs__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); display: block; margin-bottom: 16px; }
.docs__nav nav { display: flex; flex-direction: column; gap: 4px; position: sticky; top: 88px; }
.docs__nav a { font-size: 13px; color: var(--co-text-dim); padding: 6px 8px; border-left: 2px solid transparent; }
.docs__nav a:hover { color: var(--co-accent); border-color: var(--co-accent); }

.docs__body section { padding: 24px 0; border-bottom: 1px solid var(--co-border); }
.docs__body h1 { font-size: 32px; letter-spacing: -0.02em; margin-bottom: 16px; }
.docs__body h2 { font-size: 22px; margin-bottom: 12px; }
.docs__body p { color: var(--co-text-dim); line-height: 1.6; font-size: 15px; margin-bottom: 12px; }
.docs__body ol { color: var(--co-text-dim); line-height: 1.8; padding-left: 20px; font-size: 14px; }
.docs__body code {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 1px 6px; font-family: var(--co-font-mono); font-size: 12px;
}
.docs__body a { color: var(--co-accent); }

@media (max-width: 760px) {
  .docs { grid-template-columns: 1fr; gap: 24px; }
  .docs__nav nav { position: static; flex-direction: row; flex-wrap: wrap; }
}
</style>
