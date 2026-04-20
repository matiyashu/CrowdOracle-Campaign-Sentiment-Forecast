<template>
  <div class="tab">
    <header class="tab__head">
      <div>
        <span class="tab__eyebrow">IMPACT DECOMPOSITION</span>
        <h2>Impact</h2>
        <p>Four-component scorecard plus per-asset resonance.</p>
      </div>
      <button class="btn btn--ghost" @click="pickFile">Import performance data</button>
      <input ref="fileInput" type="file" accept=".csv,.json" hidden @change="onFile" />
    </header>

    <div v-if="uploadMsg" class="banner" :class="'banner--' + uploadMsg.state">{{ uploadMsg.text }}</div>

    <div v-if="loading && !data" class="skeletons">
      <LoadingSkeleton v-for="i in 4" :key="i" height="120px" />
    </div>

    <ErrorState
      v-else-if="error"
      title="Couldn't load impact."
      :body="String(error?.message || error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!data || !hasImpact"
      title="Impact score unlocks after creative and mention data are linked."
      body="Add creatives, import mentions, then return here for the full decomposition."
    >
      <router-link :to="{ name: 'CampaignCreatives' }" class="btn btn--primary">Add creatives</router-link>
      <router-link :to="{ name: 'CampaignMentions' }" class="btn btn--ghost">Import mentions</router-link>
    </EmptyState>

    <template v-else>
      <div v-if="impact.type === 'partial_estimate'" class="banner banner--warn">
        Impact score is a partial estimate. Business metrics haven't been linked yet.
      </div>

      <section class="hero">
        <div class="hero__score">
          <span>Overall impact</span>
          <strong>{{ impact.score ?? '—' }}</strong>
          <span class="hero__sub">{{ impact.type || 'scored' }}</span>
        </div>
        <div class="hero__bars">
          <div v-for="c in components" :key="c.label" class="cbar">
            <div class="cbar__head">
              <span>{{ c.label }}</span>
              <strong>{{ c.score == null ? 'n/a' : c.score }}</strong>
            </div>
            <div class="cbar__track">
              <span :style="{ width: c.score == null ? '0%' : `${Math.min(100, c.score)}%`, opacity: c.score == null ? 0.2 : 1 }"></span>
            </div>
            <p v-if="c.note" class="cbar__note">{{ c.note }}</p>
          </div>
        </div>
      </section>

      <section class="panel">
        <header class="panel__head">
          <h3>Asset scoreboard</h3>
          <span class="panel__sub">{{ assets.length }} asset{{ assets.length === 1 ? '' : 's' }}</span>
        </header>
        <div v-if="!assets.length" class="panel__empty">Add creatives to compare per-asset resonance.</div>
        <table v-else class="assets">
          <thead>
            <tr>
              <th>Asset</th>
              <th>Type</th>
              <th>Channel</th>
              <th class="num">Engagement</th>
              <th class="num">Sentiment</th>
              <th class="num">Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in assets" :key="a.asset_id || a.id">
              <td class="assets__name">{{ a.filename || a.name || `#${a.asset_id || a.id}` }}</td>
              <td>{{ a.asset_type || '—' }}</td>
              <td>{{ a.channel || '—' }}</td>
              <td class="num">{{ a.engagement_count ?? '—' }}</td>
              <td class="num" :class="sentimentClass(a.sentiment_share)">{{ pct(a.sentiment_share) }}</td>
              <td class="num" :class="scoreClass(a.score)"><strong>{{ a.score ?? '—' }}</strong></td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { analyticsApi } from '@/api/analytics'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const route = useRoute()
const analytics = useAnalyticsStore()

const campaignId = computed(() => String(route.params.campaignId))
const data = computed(() => analytics.dashboardByCampaign[campaignId.value])
const loading = computed(() => analytics.loading)
const error = computed(() => analytics.error)

const impact = computed(() => data.value?.impact || {})
const assets = computed(() => impact.value.asset_scores || [])
const hasImpact = computed(() => impact.value.score != null || (impact.value.component_scores && Object.keys(impact.value.component_scores).length))

const components = computed(() => {
  const c = impact.value.component_scores || {}
  return [
    { label: 'Conversation', score: c.conversation?.score, note: c.conversation?.note },
    { label: 'Creative',     score: c.creative?.score,     note: c.creative?.note },
    { label: 'Business',     score: c.business?.score,     note: c.business?.note },
    { label: 'Sentiment',    score: c.sentiment?.score,    note: c.sentiment?.note },
  ]
})

const fileInput = ref(null)
const uploadMsg = ref(null)

function pickFile() { fileInput.value?.click() }
async function onFile(ev) {
  const file = ev.target.files?.[0]
  ev.target.value = ''
  if (!file) return
  uploadMsg.value = { state: 'info', text: `Uploading ${file.name}…` }
  try {
    await analyticsApi.uploadPerformance(campaignId.value, file)
    uploadMsg.value = { state: 'ok', text: 'Performance data imported.' }
    reload()
  } catch (e) {
    uploadMsg.value = { state: 'err', text: e?.response?.data?.error || e.message || 'Upload failed.' }
  }
  setTimeout(() => (uploadMsg.value = null), 4000)
}

function pct(v) { return v == null ? '—' : `${Math.round(v * 100)}%` }
function sentimentClass(v) { if (v == null) return ''; if (v >= 0.5) return 'pos'; if (v <= 0.2) return 'neg'; return '' }
function scoreClass(s) { if (s == null) return ''; if (s >= 70) return 'pos'; if (s >= 40) return 'warn'; return 'neg' }

function reload() { analytics.loadDashboard(campaignId.value) }
onMounted(reload)
watch(campaignId, (id) => id && analytics.loadDashboard(id))
</script>

<style scoped>
.tab { display: flex; flex-direction: column; gap: 20px; padding: 4px 0 40px; }

.tab__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.tab__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.tab__head h2 { font-size: 20px; margin-top: 6px; letter-spacing: -0.01em; }
.tab__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 4px; }

.banner { padding: 10px 12px; border: 1px solid var(--co-border); font-size: 12px; background: var(--co-surface); }
.banner--ok { border-color: #3ecf8e; color: #3ecf8e; }
.banner--err { border-color: var(--co-danger, #ff5469); color: var(--co-danger, #ff5469); }
.banner--warn { border-color: var(--co-accent); color: var(--co-accent); }
.banner--info { color: var(--co-text-dim); }

.skeletons { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

.hero {
  display: grid; grid-template-columns: 260px 1fr; gap: 20px;
  background: var(--co-surface); border: 1px solid var(--co-border); padding: 20px;
}
@media (max-width: 820px) { .hero { grid-template-columns: 1fr; } }

.hero__score { display: flex; flex-direction: column; gap: 4px; justify-content: center; }
.hero__score span { font-size: 11px; letter-spacing: 0.12em; color: var(--co-text-dim); text-transform: uppercase; }
.hero__score strong { font-size: 56px; color: var(--co-accent); letter-spacing: -0.02em; }
.hero__sub { font-size: 11px; color: var(--co-text-dim); }

.hero__bars { display: flex; flex-direction: column; gap: 12px; }
.cbar { display: flex; flex-direction: column; gap: 4px; }
.cbar__head { display: flex; justify-content: space-between; font-size: 12px; }
.cbar__head strong { color: var(--co-text); }
.cbar__track { background: var(--co-bg); height: 8px; }
.cbar__track span { display: block; height: 100%; background: var(--co-accent); }
.cbar__note { font-size: 11px; color: var(--co-text-dim); margin: 0; }

.panel {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.panel__head { display: flex; justify-content: space-between; align-items: center; }
.panel__head h3 { font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--co-text-dim); }
.panel__sub { font-size: 11px; color: var(--co-text-mute, #666); }
.panel__empty { font-size: 12px; color: var(--co-text-mute, #666); padding: 24px 0; text-align: center; }

.assets { width: 100%; border-collapse: collapse; font-size: 12px; }
.assets th {
  text-align: left; font-size: 10px; letter-spacing: 0.1em;
  color: var(--co-text-dim); padding: 8px 6px;
  border-bottom: 1px solid var(--co-border); text-transform: uppercase;
}
.assets td { padding: 10px 6px; border-bottom: 1px solid var(--co-border); color: var(--co-text); }
.assets .num { text-align: right; }
.assets .num.pos { color: #3ecf8e; }
.assets .num.warn { color: var(--co-accent); }
.assets .num.neg { color: #ff5469; }
.assets__name { font-family: var(--co-font-mono); }

.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
