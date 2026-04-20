<template>
  <div class="pricing">
    <header class="pricing__head">
      <span class="pricing__eyebrow">PRICING</span>
      <h1>Pick the tier that matches your launch cadence.</h1>
      <p>Every plan includes the full analytics stack. You pay for scale, seats, and support.</p>
    </header>

    <section class="tiers">
      <article class="tier">
        <h2>Free</h2>
        <p class="tier__price">$0<span>/mo</span></p>
        <ul>
          <li>1 workspace · 1 seat</li>
          <li>3 campaigns</li>
          <li>500 mentions / mo</li>
          <li>Bring-your-own AI provider</li>
          <li>Community support</li>
        </ul>
        <router-link to="/app/demo" class="btn btn--ghost">Start free</router-link>
      </article>

      <article class="tier tier--featured">
        <span class="tier__flag">MOST POPULAR</span>
        <h2>Pro</h2>
        <p class="tier__price">$149<span>/mo</span></p>
        <ul>
          <li>Unlimited campaigns</li>
          <li>Up to 10 seats</li>
          <li>50k mentions / mo</li>
          <li>Reality Seeds simulations</li>
          <li>Priority email support</li>
        </ul>
        <router-link to="/app/demo" class="btn btn--primary">Start Pro trial</router-link>
      </article>

      <article class="tier">
        <h2>Enterprise</h2>
        <p class="tier__price">Custom</p>
        <ul>
          <li>Unlimited mentions</li>
          <li>SSO + role-based access</li>
          <li>Dedicated simulation capacity</li>
          <li>On-prem / VPC deploy</li>
          <li>Named customer success</li>
        </ul>
        <a href="mailto:hello@crowdoracle.ai" class="btn btn--ghost">Talk to sales</a>
      </article>
    </section>

    <section class="faq">
      <h2>Common questions</h2>
      <dl>
        <dt>Do I need my own OpenAI / Anthropic key?</dt>
        <dd>Yes. CrowdOracle routes to the provider you configure so you pay model cost directly and control data residency.</dd>
        <dt>Is there a free trial of Pro?</dt>
        <dd>Pro comes with a 14-day trial — no card required.</dd>
        <dt>What counts as a mention?</dt>
        <dd>One row of listening data (social post, review, forum comment). CSV imports and connected sources both count.</dd>
      </dl>
    </section>
  </div>
</template>

<style scoped>
.pricing { color: var(--co-text); padding-bottom: 80px; }
.pricing__head { text-align: center; padding: 80px 32px 40px; max-width: 720px; margin: 0 auto; }
.pricing__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.pricing__head h1 { font-size: clamp(32px, 4vw, 46px); margin: 16px 0; letter-spacing: -0.02em; }
.pricing__head p { color: var(--co-text-dim); font-size: 15px; }

.tiers {
  display: grid; gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  max-width: 1100px; margin: 0 auto; padding: 20px 32px 60px;
}
.tier {
  position: relative;
  padding: 32px 24px;
  background: var(--co-surface);
  border: 1px solid var(--co-border);
  display: flex; flex-direction: column;
}
.tier--featured { border-color: var(--co-accent); }
.tier__flag {
  position: absolute; top: -10px; left: 24px;
  background: var(--co-accent); color: #000;
  font-size: 10px; letter-spacing: 0.1em; font-weight: 600;
  padding: 3px 8px;
}
.tier h2 { font-size: 18px; margin-bottom: 8px; }
.tier__price { font-size: 34px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 20px; }
.tier__price span { font-size: 14px; color: var(--co-text-dim); font-weight: 400; }
.tier ul { list-style: none; margin-bottom: 24px; flex: 1; }
.tier li { font-size: 14px; color: var(--co-text-dim); padding: 6px 0; border-bottom: 1px solid var(--co-border); }
.tier li:last-child { border-bottom: none; }

.btn {
  padding: 12px 18px; text-align: center;
  font-family: var(--co-font-mono); font-size: 13px;
  border: 1px solid var(--co-border-2);
  background: var(--co-surface);
  color: var(--co-text);
  border-radius: var(--co-radius);
  letter-spacing: 0.02em;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }

.faq { max-width: 720px; margin: 0 auto; padding: 40px 32px; }
.faq h2 { font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--co-text-dim); margin-bottom: 20px; }
.faq dt { font-size: 15px; margin-top: 20px; color: var(--co-text); }
.faq dd { font-size: 14px; color: var(--co-text-dim); line-height: 1.6; margin-top: 6px; padding-bottom: 16px; border-bottom: 1px solid var(--co-border); }
</style>
