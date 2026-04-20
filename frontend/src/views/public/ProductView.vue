<template>
  <div class="prod">
    <header class="prod__head">
      <span class="prod__eyebrow">PRODUCT TOUR</span>
      <h1>Four surfaces. One intelligence loop.</h1>
    </header>

    <section class="feat">
      <div class="feat__text">
        <span class="feat__num">01</span>
        <h2>Dashboard-first campaign workspace</h2>
        <p>Every campaign opens on an executive overview — mentions, sentiment, impact, and next-move recommendations. Drill into Creatives, Mentions, Sentiment, Impact, or Report as dedicated tabs.</p>
      </div>
      <div class="feat__visual">Overview · Creatives · Mentions · Sentiment · Impact · Report</div>
    </section>

    <section class="feat feat--alt">
      <div class="feat__text">
        <span class="feat__num">02</span>
        <h2>Creative intelligence</h2>
        <p>Drop in image, video, or copy. We run OCR on stills, transcribe audio, pull hooks and CTAs, and attribute downstream conversation back to the asset that drove it.</p>
      </div>
      <div class="feat__visual">OCR · Transcript · Visual summary · Hook · CTA · Emotional tone</div>
    </section>

    <section class="feat">
      <div class="feat__text">
        <span class="feat__num">03</span>
        <h2>Reality Seeds simulation</h2>
        <p>Upload a brief. Persona-driven agents rehearse it on a simulated Twitter and Reddit. You see the sentiment shape, topic clusters, and risk vectors <em>before</em> spend.</p>
      </div>
      <div class="feat__visual">Graph · Split · Workbench · Agent timeline</div>
    </section>

    <section class="feat feat--alt">
      <div class="feat__text">
        <span class="feat__num">04</span>
        <h2>Provider routing</h2>
        <p>Bring the model you trust — OpenAI, Anthropic, Qwen, Gemini, or any OpenAI-compatible endpoint. Route per task: creative vision, sentiment, reports, simulation, transcription.</p>
      </div>
      <div class="feat__visual">Providers · Routing matrix · Fallbacks · Test connection</div>
    </section>

    <section class="cta">
      <h2>See it with real data.</h2>
      <router-link to="/app/demo" class="btn btn--primary">Load a demo campaign</router-link>
    </section>
  </div>
</template>

<style scoped>
.prod { color: var(--co-text); padding-bottom: 80px; }
.prod__head { text-align: center; padding: 80px 32px 40px; }
.prod__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.prod__head h1 { font-size: clamp(32px, 4vw, 48px); margin-top: 16px; letter-spacing: -0.02em; }

.feat {
  display: grid; gap: 40px;
  grid-template-columns: 1fr 1fr;
  max-width: 1100px; margin: 0 auto;
  padding: 60px 32px;
  align-items: center;
}
.feat--alt .feat__text { order: 2; }
.feat__num { font-size: 11px; color: var(--co-accent); letter-spacing: 0.1em; }
.feat__text h2 { font-size: 26px; margin: 12px 0 16px; }
.feat__text p { font-size: 15px; line-height: 1.6; color: var(--co-text-dim); }
.feat__text p em { color: var(--co-text); font-style: normal; text-decoration: underline; text-decoration-color: var(--co-accent); }
.feat__visual {
  padding: 48px 24px;
  background: var(--co-surface);
  border: 1px solid var(--co-border);
  text-align: center;
  color: var(--co-text-dim);
  font-size: 12px; letter-spacing: 0.08em;
  text-transform: uppercase;
}

.cta { text-align: center; padding: 60px 32px; border-top: 1px solid var(--co-border); }
.cta h2 { font-size: 24px; margin-bottom: 20px; }
.btn { padding: 12px 22px; font-family: var(--co-font-mono); font-size: 13px; border: 1px solid var(--co-accent); background: var(--co-accent); color: #000; border-radius: var(--co-radius); cursor: pointer; }
.btn:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); }

@media (max-width: 760px) {
  .feat { grid-template-columns: 1fr; }
  .feat--alt .feat__text { order: 0; }
}
</style>
