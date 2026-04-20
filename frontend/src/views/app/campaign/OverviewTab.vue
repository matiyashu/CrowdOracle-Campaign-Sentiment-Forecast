<template>
  <div class="ov">
    <div v-if="loading && !data" class="ov__skeletons">
      <LoadingSkeleton v-for="i in 6" :key="i" height="80px" />
    </div>

    <ErrorState
      v-else-if="error"
      title="Couldn't load the dashboard."
      :body="String(error?.message || error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!data"
      title="No analytics yet."
      body="Upload mentions and creatives to populate this dashboard."
    >
      <router-link :to="{ name: 'CampaignCreatives' }" class="btn btn--primary">Add creatives</router-link>
      <router-link :to="{ name: 'CampaignMentions' }" class="btn btn--ghost">Import mentions</router-link>
    </EmptyState>

    <template v-else>
      <!-- KPI cards -->
      <section class="kpis">
        <div class="kpi"><span>Total mentions</span><strong>{{ overview.total_mentions ?? 0 }}</strong></div>
        <div class="kpi"><span>Positive</span><strong class="kpi--pos">{{ pct(overview.positive_share) }}</strong></div>
        <div class="kpi"><span>Negative</span><strong class="kpi--neg">{{ pct(overview.negative_share) }}</strong></div>
        <div class="kpi">
          <span>Impact score
            <AppBadge v-if="overview.impact_type === 'partial_estimate'" tone="warn">partial</AppBadge>
          </span>
          <strong class="kpi--accent">{{ overview.impact_score ?? '—' }}</strong>
        </div>
        <div class="kpi"><span>Top theme</span><strong class="kpi--small">{{ overview.top_theme || '—' }}</strong></div>
        <div class="kpi"><span>Biggest risk</span><strong class="kpi--small kpi--neg">{{ overview.biggest_risk || '—' }}</strong></div>
      </section>

      <!-- Sentiment trend + Recommendations -->
      <section class="row row--8-4">
        <div class="panel">
          <header class="panel__head">
            <h3>Sentiment trend</h3>
            <router-link :to="{ name: 'CampaignSentiment' }" class="panel__link">View all →</router-link>
          </header>
          <div v-if="!sentiment.by_day?.length" class="panel__empty">No mentions in this date range yet.</div>
          <svg v-else class="trend" viewBox="0 0 600 200" preserveAspectRatio="none">
            <line x1="0" y1="100" x2="600" y2="100" stroke="var(--co-border)" stroke-dasharray="4,4" />
            <polyline :points="trendPoints('positive_share')" fill="none" stroke="#3ecf8e" stroke-width="2" />
            <polyline :points="trendPoints('negative_share')" fill="none" stroke="#ff5469" stroke-width="2" />
          </svg>
          <div class="legend">
            <span><i class="dot" style="background:#3ecf8e"></i> positive</span>
            <span><i class="dot" style="background:#ff5469"></i> negative</span>
          </div>
        </div>

        <div class="panel">
          <header class="panel__head">
            <h3>Top recommendations</h3>
            <router-link :to="{ name: 'CampaignReport' }" class="panel__link">Full report →</router-link>
          </header>
          <div v-if="!topRecs.length" class="panel__empty">Analysis surfaces actions once mentions are ingested.</div>
          <ol v-else class="recs">
            <li v-for="(r, i) in topRecs" :key="i">
              <span class="recs__bucket" :class="`recs__bucket--${r.bucket}`">{{ r.bucket }}</span>
              <strong>{{ r.title }}</strong>
              <p>{{ r.detail }}</p>
            </li>
          </ol>
        </div>
      </section>

      <!-- Aspect bars + Keywords -->
      <section class="row row--6-6">
        <div class="panel">
          <header class="panel__head">
            <h3>Sentiment by aspect</h3>
            <router-link :to="{ name: 'CampaignSentiment' }" class="panel__link">View all →</router-link>
          </header>
          <div v-if="!sentiment.by_aspect?.length" class="panel__empty">Aspect sentiment appears after the first analysis run.</div>
          <ul v-else class="aspects">
            <li v-for="(a, i) in sentiment.by_aspect.slice(0, 6)" :key="i">
              <div class="aspects__name">{{ a.aspect }} <span>({{ a.total }})</span></div>
              <div class="aspects__bar">
                <span class="seg seg--pos" :style="{ width: pct(a.positive_share) }" />
                <span class="seg seg--neu" :style="{ width: pct(a.neutral_share) }" />
                <span class="seg seg--neg" :style="{ width: pct(a.negative_share) }" />
              </div>
            </li>
          </ul>
        </div>

        <div class="panel">
          <header class="panel__head">
            <h3>Top phrases</h3>
            <router-link :to="{ name: 'CampaignMentions' }" class="panel__link">View all →</router-link>
          </header>
          <div v-if="!keywords.top_phrases?.length" class="panel__empty">Upload mentions to see what people are saying.</div>
          <ul v-else class="phrases">
            <li v-for="(p, i) in keywords.top_phrases.slice(0, 8)" :key="i">
              <span class="phrases__term">{{ p.phrase }}</span>
              <span class="phrases__bar"><span :style="{ width: barW(p.count, maxPhrase) }" /></span>
              <span class="phrases__count">{{ p.count }}</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- Impact decomposition + Asset scoreboard -->
      <section class="row row--7-5">
        <div class="panel">
          <header class="panel__head">
            <h3>Impact decomposition</h3>
            <router-link :to="{ name: 'CampaignImpact' }" class="panel__link">View all →</router-link>
          </header>
          <ul class="impact">
            <li v-for="(c, key) in impactBars" :key="key">
              <span class="impact__label">{{ key }}</span>
              <span class="impact__bar"><span :style="impactBarStyle(c.score)" /></span>
              <span class="impact__score">{{ c.score == null ? 'n/a' : c.score }}</span>
            </li>
          </ul>
        </div>

        <div class="panel">
          <header class="panel__head">
            <h3>Top assets</h3>
            <router-link :to="{ name: 'CampaignImpact' }" class="panel__link">View all →</router-link>
          </header>
          <div v-if="!assetScores.length" class="panel__empty">Add creatives to compare per-asset resonance.</div>
          <table v-else class="assets">
            <thead><tr><th>Asset</th><th>Type</th><th>+ / −</th><th>Score</th></tr></thead>
            <tbody>
              <tr v-for="a in assetScores" :key="a.asset_id">
                <td class="assets__name">{{ a.filename || a.asset_id?.slice(0,8) }}</td>
                <td>{{ a.asset_type }}</td>
                <td><span class="kpi--pos">{{ a.positive }}</span> / <span class="kpi--neg">{{ a.negative }}</span></td>
                <td><strong :class="scoreClass(a.score)">{{ a.score }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="cta">
        <h3>Ready to ship the report?</h3>
        <router-link :to="{ name: 'CampaignReport' }" class="btn btn--primary">Open report builder</router-link>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import AppBadge from '@/components/common/AppBadge.vue'

const route = useRoute()
const analytics = useAnalyticsStore()

const campaignId = computed(() => String(route.params.campaignId))
const data = computed(() => analytics.dashboardByCampaign[campaignId.value])
const loading = computed(() => analytics.loading)
const error = computed(() => analytics.error)

const overview = computed(() => data.value?.overview || {})
const sentiment = computed(() => data.value?.sentiment || {})
const keywords = computed(() => data.value?.keywords || {})
const recs = computed(() => data.value?.recommendations || [])
const topRecs = computed(() => recs.value.slice(0, 3))
const assetScores = computed(() => (data.value?.impact?.asset_scores || []).slice(0, 5))

const maxPhrase = computed(() => {
  const list = keywords.value.top_phrases || []
  return Math.max(1, ...list.map((p) => p.count))
})

const impactBars = computed(() => {
  const c = data.value?.impact?.component_scores || {}
  return {
    Conversation: { score: c.conversation?.score },
    Creative: { score: c.creative?.score },
    Business: { score: c.business?.score },
    Sentiment: { score: c.sentiment?.score },
  }
})

function pct(v) {
  if (v == null) return '—'
  return `${Math.round(v * 100)}%`
}
function barW(v, max) { return `${Math.max(2, Math.round((v / max) * 100))}%` }
function trendPoints(field) {
  const days = sentiment.value.by_day || []
  if (!days.length) return ''
  const W = 600, H = 200
  const xStep = days.length > 1 ? W / (days.length - 1) : W
  return days.map((d, i) => {
    const v = d[field] ?? 0
    return `${(i * xStep).toFixed(1)},${(H - v * H).toFixed(1)}`
  }).join(' ')
}
function impactBarStyle(score) {
  return { width: score == null ? '0%' : `${Math.min(100, score)}%`, opacity: score == null ? 0.2 : 1 }
}
function scoreClass(s) {
  if (s == null) return ''
  if (s >= 70) return 'kpi--pos'
  if (s >= 40) return 'kpi--accent'
  return 'kpi--neg'
}

function reload() { analytics.loadDashboard(campaignId.value) }
onMounted(reload)
watch(campaignId, (id) => id && analytics.loadDashboard(id))
</script>

<style scoped>
.ov { display: flex; flex-direction: column; gap: 20px; padding: 16px 0; }
.ov__skeletons { display: grid; gap: 12px; grid-template-columns: repeat(3, 1fr); }

.kpis { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
.kpi {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 14px; display: flex; flex-direction: column; gap: 6px;
}
.kpi span { font-size: 10px; letter-spacing: 0.1em; color: var(--co-text-dim); text-transform: uppercase; display: flex; gap: 6px; align-items: center; }
.kpi strong { font-size: 22px; letter-spacing: -0.01em; }
.kpi--small { font-size: 13px !important; }
.kpi--pos { color: #3ecf8e; }
.kpi--neg { color: #ff5469; }
.kpi--accent { color: var(--co-accent); }

.row { display: grid; gap: 14px; }
.row--8-4 { grid-template-columns: 2fr 1fr; }
.row--6-6 { grid-template-columns: 1fr 1fr; }
.row--7-5 { grid-template-columns: 1.4fr 1fr; }

.panel {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.panel__head { display: flex; justify-content: space-between; align-items: center; }
.panel__head h3 { font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--co-text-dim); }
.panel__link { font-size: 11px; color: var(--co-accent); }
.panel__empty { font-size: 12px; color: var(--co-text-mute); padding: 24px 0; text-align: center; }

.trend { width: 100%; height: 200px; }
.legend { display: flex; gap: 14px; font-size: 11px; color: var(--co-text-dim); }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }

.recs { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.recs li { padding: 10px; background: var(--co-bg); border: 1px solid var(--co-border); }
.recs strong { display: block; font-size: 13px; margin: 4px 0; }
.recs p { font-size: 12px; color: var(--co-text-dim); line-height: 1.5; }
.recs__bucket {
  font-size: 9px; letter-spacing: 0.15em; padding: 2px 6px;
  border: 1px solid var(--co-border-2); color: var(--co-text-dim); text-transform: uppercase;
}
.recs__bucket--scale { color: #3ecf8e; border-color: #3ecf8e; }
.recs__bucket--optimize { color: var(--co-accent); border-color: var(--co-accent); }
.recs__bucket--rework { color: #ff5469; border-color: #ff5469; }
.recs__bucket--investigate { color: var(--co-text-dim); }

.aspects { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.aspects__name { font-size: 12px; display: flex; gap: 6px; margin-bottom: 4px; }
.aspects__name span { color: var(--co-text-dim); }
.aspects__bar { display: flex; height: 8px; background: var(--co-bg); }
.seg { display: block; }
.seg--pos { background: #3ecf8e; }
.seg--neu { background: var(--co-border-2); }
.seg--neg { background: #ff5469; }

.phrases { list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 12px; }
.phrases li { display: grid; grid-template-columns: 1fr 80px 30px; gap: 8px; align-items: center; }
.phrases__term { color: var(--co-text); }
.phrases__bar { background: var(--co-bg); height: 6px; }
.phrases__bar span { display: block; height: 100%; background: var(--co-accent); }
.phrases__count { font-size: 11px; color: var(--co-text-dim); text-align: right; }

.impact { list-style: none; display: flex; flex-direction: column; gap: 10px; font-size: 12px; }
.impact li { display: grid; grid-template-columns: 100px 1fr 40px; gap: 12px; align-items: center; }
.impact__bar { background: var(--co-bg); height: 6px; }
.impact__bar span { display: block; height: 100%; background: var(--co-accent); }
.impact__score { font-size: 12px; text-align: right; color: var(--co-text); }

.assets { width: 100%; border-collapse: collapse; font-size: 12px; }
.assets th { text-align: left; font-size: 10px; letter-spacing: 0.1em; color: var(--co-text-dim); padding: 6px 4px; border-bottom: 1px solid var(--co-border); text-transform: uppercase; }
.assets td { padding: 8px 4px; border-bottom: 1px solid var(--co-border); }
.assets__name { font-family: var(--co-font-mono); }

.cta {
  text-align: center; padding: 24px;
  background: var(--co-surface); border: 1px solid var(--co-border);
  display: flex; flex-direction: column; gap: 12px; align-items: center;
}
.cta h3 { font-size: 14px; letter-spacing: -0.01em; }

.btn {
  padding: 10px 18px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-accent); background: var(--co-accent); color: #000;
  border-radius: var(--co-radius); display: inline-block;
}
.btn:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); }
.btn--ghost { background: transparent; color: var(--co-text); border-color: var(--co-border-2); }
.btn--ghost:hover { color: var(--co-accent); border-color: var(--co-accent); background: transparent; }
.btn--primary { background: var(--co-accent); color: #000; }

@media (max-width: 1100px) {
  .kpis { grid-template-columns: repeat(3, 1fr); }
  .row--8-4, .row--6-6, .row--7-5 { grid-template-columns: 1fr; }
  .ov__skeletons { grid-template-columns: 1fr 1fr; }
}
</style>
