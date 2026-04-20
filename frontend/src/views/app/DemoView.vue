<template>
  <section class="demo">
    <header class="demo__head">
      <span class="demo__eyebrow">DEMO MODE</span>
      <h1>Explore CrowdOracle with preloaded campaigns.</h1>
      <p>
        Pick a package below. We'll seed a demo campaign with creative analysis, mention sentiment, and
        performance metrics — so you can walk every feature before uploading a thing.
      </p>
    </header>

    <div v-if="store.active && store.campaignId" class="banner banner--ok">
      Demo loaded · <router-link :to="`/app/campaigns/${store.campaignId}/overview`">open the seeded campaign</router-link>
      · <button class="linklike" @click="handleReset">reset demo data</button>
    </div>

    <div v-if="store.error" class="banner banner--err">{{ store.error }}</div>

    <div v-if="loadingList" class="grid">
      <div v-for="n in 3" :key="n" class="card card--skeleton" />
    </div>

    <div v-else-if="!store.packages.length" class="empty">
      <strong>No demo packages found.</strong>
      <span>Your backend has no files under <code>backend/app/demo/packages/</code>.</span>
    </div>

    <div v-else class="grid">
      <article
        v-for="pkg in store.packages"
        :key="pkg.package_id"
        class="card"
        :class="{ 'card--busy': busyId === pkg.package_id }"
      >
        <header class="card__head">
          <span class="card__brand">{{ pkg.brand || '—' }}</span>
          <h2>{{ pkg.title }}</h2>
        </header>
        <p class="card__desc">{{ pkg.description }}</p>

        <dl class="meta">
          <div>
            <dt>Markets</dt>
            <dd>{{ (pkg.markets || []).join(', ') || '—' }}</dd>
          </div>
          <div>
            <dt>Channels</dt>
            <dd>{{ (pkg.channels || []).join(', ') || '—' }}</dd>
          </div>
        </dl>

        <footer class="card__foot">
          <button
            class="btn btn--primary"
            :disabled="busyId !== null"
            @click="handleLoad(pkg.package_id)"
          >
            {{ busyId === pkg.package_id ? 'Seeding…' : 'Load this demo' }}
          </button>
        </footer>
      </article>
    </div>

    <section class="note">
      <strong>How demo mode works</strong>
      <p>
        Each package seeds a fresh campaign tagged <code>demo</code>. Nothing you do inside a demo campaign
        affects real data. Click <em>reset</em> above — or hit the button below — to wipe every demo campaign
        in this workspace.
      </p>
      <button class="btn btn--ghost" :disabled="resetting" @click="handleResetAll">
        {{ resetting ? 'Resetting…' : 'Reset all demo data' }}
      </button>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDemoStore } from '@/stores/demo'

const router = useRouter()
const store = useDemoStore()

const loadingList = ref(false)
const busyId = ref(null)
const resetting = ref(false)

async function fetchList() {
  loadingList.value = true
  try { await store.loadPackages() } finally { loadingList.value = false }
}

async function handleLoad(pkgId) {
  busyId.value = pkgId
  try {
    const campaignId = await store.load(pkgId)
    if (campaignId) router.push(`/app/campaigns/${campaignId}/overview`)
  } catch (_) {
    // error is exposed via store.error
  } finally {
    busyId.value = null
  }
}

async function handleReset() {
  if (!store.campaignId) return
  resetting.value = true
  try { await store.reset(store.campaignId) } finally { resetting.value = false }
}

async function handleResetAll() {
  resetting.value = true
  try { await store.reset() } finally { resetting.value = false }
}

onMounted(() => {
  store.hydrate()
  fetchList()
})
</script>

<style scoped>
.demo { display: flex; flex-direction: column; gap: 24px; }
.demo__head { display: flex; flex-direction: column; gap: 6px; max-width: 720px; }
.demo__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.demo__head h1 { font-size: 22px; letter-spacing: -0.01em; }
.demo__head p { font-size: 13px; color: var(--co-text-dim); line-height: 1.55; }

.banner {
  padding: 10px 14px; border: 1px solid var(--co-border);
  font-size: 12px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
}
.banner--ok  { border-color: #3ecf8e; color: #3ecf8e; }
.banner--err { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }
.banner a { color: inherit; text-decoration: underline; }
.linklike {
  background: none; border: none; color: inherit;
  text-decoration: underline; cursor: pointer; padding: 0; font: inherit;
}

.grid {
  display: grid; gap: 14px;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.card {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 18px; display: flex; flex-direction: column; gap: 12px;
  transition: border-color 0.15s;
}
.card:hover { border-color: var(--co-accent); }
.card--busy { opacity: 0.7; pointer-events: none; }
.card--skeleton { min-height: 220px; animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 0.55; } 50% { opacity: 0.9; } }

.card__head { display: flex; flex-direction: column; gap: 4px; }
.card__brand { font-size: 10px; letter-spacing: 0.15em; color: var(--co-text-dim); text-transform: uppercase; }
.card__head h2 { font-size: 15px; letter-spacing: -0.01em; color: var(--co-text); }
.card__desc { font-size: 12px; color: var(--co-text-dim); line-height: 1.5; }

.meta { display: flex; gap: 18px; margin: 0; padding: 0; }
.meta > div { display: flex; flex-direction: column; gap: 2px; }
.meta dt { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--co-text-dim); }
.meta dd { margin: 0; font-size: 12px; color: var(--co-text); font-family: var(--co-font-mono); }

.card__foot { margin-top: auto; display: flex; justify-content: flex-end; }

.empty {
  border: 1px dashed var(--co-border-2); padding: 20px;
  display: flex; flex-direction: column; gap: 4px;
}
.empty strong { font-size: 13px; }
.empty span { font-size: 12px; color: var(--co-text-dim); }
.empty code { font-family: var(--co-font-mono); font-size: 11px; }

.note {
  border: 1px solid var(--co-border); padding: 16px;
  display: flex; flex-direction: column; gap: 10px; max-width: 720px;
}
.note strong { font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--co-text-dim); }
.note p { font-size: 12px; color: var(--co-text-dim); line-height: 1.55; }
.note code { font-family: var(--co-font-mono); font-size: 11px; }
.note em { color: var(--co-accent); font-style: normal; }

.btn {
  padding: 8px 14px; font-family: var(--co-font-mono); font-size: 11px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2, var(--co-accent)); color: #000; }
.btn--ghost { background: transparent; align-self: flex-start; }
</style>
