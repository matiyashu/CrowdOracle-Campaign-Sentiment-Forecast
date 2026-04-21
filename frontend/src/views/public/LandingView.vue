<template>
  <div class="landing">
    <section class="hero">
      <div class="hero__inner">
        <span class="hero__eyebrow">MARKETING INTELLIGENCE · MULTI-AGENT FORECASTING</span>
        <h1 class="hero__headline">See the reaction <span class="accent">before</span> you ship the campaign.</h1>
        <p class="hero__sub">
          CrowdOracle simulates how real audiences will talk about your creative —
          and scores what actually moves the needle when it goes live.
        </p>
        <div class="hero__cta">
          <router-link to="/app/demo" class="btn btn--primary">Start with a demo campaign</router-link>
          <router-link to="/product" class="btn btn--ghost">See how it works →</router-link>
        </div>
      </div>
    </section>

    <section class="tiles">
      <article class="tile">
        <h3>01 · Creative intelligence</h3>
        <p>Upload your ads. We extract hooks, OCR copy, transcribe video, and tell you which assets earn positive conversation.</p>
      </article>
      <article class="tile">
        <h3>02 · Reality Seeds simulation</h3>
        <p>Drop in a brief. Hundreds of persona-driven agents rehearse your launch on simulated Twitter and Reddit so you see the sentiment shape before a cent is spent.</p>
      </article>
      <article class="tile">
        <h3>03 · Bring your own AI</h3>
        <p>Route every task to the model you trust. OpenAI, Anthropic, Qwen, Gemini, or your own endpoint. Per-task, not per-app.</p>
      </article>
    </section>

    <section class="how">
      <h2>How it works</h2>
      <ol>
        <li><strong>Import.</strong> Campaign brief, creatives, mentions, and performance data in one upload pass.</li>
        <li><strong>Analyze.</strong> Multimodal creative breakdown + mention keyword/sentiment aggregation.</li>
        <li><strong>Simulate.</strong> Optional Reality Seeds run to forecast audience reaction.</li>
        <li><strong>Decide.</strong> Impact score + a ranked list of scale / optimize / rework / investigate actions.</li>
      </ol>
    </section>

    <section class="closer">
      <h2>Your next campaign deserves a second opinion.</h2>
      <router-link to="/app/demo" class="btn btn--primary">Load a demo campaign — no signup.</router-link>
    </section>

    <footer class="foot">
      <span class="foot__brand">▶ CROWDORACLE</span>
      <nav>
        <router-link to="/product">Product</router-link>
        <router-link to="/docs">Docs</router-link>
      </nav>
      <span class="foot__by">© 2026 · Built by Prima Hanura Akbar</span>
    </footer>
  </div>
</template>

<style scoped>
.landing { color: var(--co-text); }
.accent { color: var(--co-accent); }

.hero {
  padding: 120px 32px 80px;
  text-align: center;
  background: radial-gradient(ellipse at top, rgba(255,106,0,0.08), transparent 70%);
}
.hero__inner { max-width: 820px; margin: 0 auto; }
.hero__eyebrow {
  font-size: 11px; letter-spacing: 0.15em;
  color: var(--co-text-dim);
}
.hero__headline {
  font-size: clamp(36px, 5vw, 58px);
  line-height: 1.08;
  margin: 24px 0;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.hero__sub {
  font-size: 16px; line-height: 1.5;
  color: var(--co-text-dim);
  max-width: 620px;
  margin: 0 auto 32px;
}
.hero__cta { display: inline-flex; gap: 12px; flex-wrap: wrap; justify-content: center; }

.btn {
  padding: 12px 22px;
  font-family: var(--co-font-mono);
  font-size: 13px;
  border: 1px solid var(--co-border-2);
  background: var(--co-surface);
  color: var(--co-text);
  border-radius: var(--co-radius);
  cursor: pointer;
  letter-spacing: 0.02em;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }

.tiles {
  padding: 48px 32px;
  display: grid; gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  max-width: 1200px; margin: 0 auto;
}
.tile {
  padding: 28px;
  border: 1px solid var(--co-border);
  background: var(--co-surface);
}
.tile h3 {
  font-size: 13px; letter-spacing: 0.05em;
  color: var(--co-accent);
  margin-bottom: 12px;
  text-transform: uppercase;
}
.tile p {
  font-size: 14px; line-height: 1.5;
  color: var(--co-text-dim);
}

.how {
  padding: 64px 32px;
  max-width: 820px; margin: 0 auto;
}
.how h2 {
  font-size: 11px; letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--co-text-dim);
  margin-bottom: 20px;
}
.how ol {
  counter-reset: step;
  list-style: none;
}
.how li {
  padding: 16px 0;
  border-bottom: 1px solid var(--co-border);
  font-size: 15px; line-height: 1.5;
  color: var(--co-text-dim);
}
.how li strong { color: var(--co-text); }

.closer {
  padding: 80px 32px;
  text-align: center;
  border-top: 1px solid var(--co-border);
  background: var(--co-surface);
}
.closer h2 {
  font-size: clamp(22px, 3vw, 30px);
  margin-bottom: 24px;
  letter-spacing: -0.01em;
}

.foot {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 32px;
  border-top: 1px solid var(--co-border);
  font-size: 11px;
  color: var(--co-text-mute);
  flex-wrap: wrap; gap: 12px;
}
.foot nav { display: flex; gap: 16px; }
.foot nav a { color: var(--co-text-dim); }
.foot nav a:hover { color: var(--co-accent); }
.foot__brand { color: var(--co-text); letter-spacing: 0.08em; }
</style>
