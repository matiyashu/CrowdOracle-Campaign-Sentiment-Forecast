<template>
  <div class="dash-container">
    <nav class="navbar">
      <div class="nav-brand">BIGBROTHER</div>
      <div class="nav-links">
        <router-link to="/campaigns" class="nav-link">← Campaigns</router-link>
        <router-link :to="`/campaign/${campaignId}`" class="nav-link">Detail</router-link>
        <router-link :to="`/campaign/${campaignId}/creatives`" class="nav-link">Creatives</router-link>
      </div>
    </nav>

    <div v-if="loading" class="state-msg">Loading dashboard…</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>

    <div v-else-if="data" class="page-content">
      <!-- Header -->
      <header class="page-header">
        <span class="orange-tag">CAMPAIGN INTELLIGENCE</span>
        <h1 class="page-title">{{ data.campaign.name }}</h1>
        <p class="page-desc">{{ data.campaign.brand }} · {{ data.campaign.objective || '—' }}</p>
      </header>

      <!-- Overview cards -->
      <section class="cards-row">
        <div class="card">
          <div class="card-label">TOTAL MENTIONS</div>
          <div class="card-value">{{ data.overview.total_mentions }}</div>
        </div>
        <div class="card">
          <div class="card-label">POSITIVE</div>
          <div class="card-value positive">{{ pct(data.overview.positive_share) }}</div>
        </div>
        <div class="card">
          <div class="card-label">NEGATIVE</div>
          <div class="card-value negative">{{ pct(data.overview.negative_share) }}</div>
        </div>
        <div class="card impact">
          <div class="card-label">IMPACT SCORE
            <span v-if="data.overview.impact_type === 'partial_estimate'" class="badge">partial</span>
          </div>
          <div class="card-value accent">{{ data.overview.impact_score ?? '—' }}</div>
        </div>
        <div class="card">
          <div class="card-label">TOP THEME</div>
          <div class="card-value small">{{ data.overview.top_theme || '—' }}</div>
        </div>
        <div class="card">
          <div class="card-label">BIGGEST RISK</div>
          <div class="card-value small risk">{{ data.overview.biggest_risk || '—' }}</div>
        </div>
      </section>

      <!-- Row: keywords + sentiment trend -->
      <section class="grid-2">
        <div class="panel">
          <h2 class="panel-title">Top phrases</h2>
          <div v-if="!data.keywords.top_phrases?.length" class="panel-empty">No phrases yet — upload mentions.</div>
          <div v-else class="bar-list">
            <div v-for="(p, i) in data.keywords.top_phrases.slice(0, 10)" :key="i" class="bar-row">
              <div class="bar-label">{{ p.phrase }}</div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: barWidth(p.count, maxPhraseCount) }"></div>
              </div>
              <div class="bar-count">{{ p.count }}</div>
            </div>
          </div>
        </div>

        <div class="panel">
          <h2 class="panel-title">Sentiment trend</h2>
          <div v-if="!data.sentiment.by_day?.length" class="panel-empty">No dated mentions yet.</div>
          <svg v-else class="trend-svg" viewBox="0 0 600 220" preserveAspectRatio="none">
            <polyline
              :points="trendPoints('positive_share', '#0f0')"
              fill="none" stroke="#0f0" stroke-width="2"
            />
            <polyline
              :points="trendPoints('negative_share', '#f44')"
              fill="none" stroke="#f44" stroke-width="2"
            />
            <line x1="0" y1="110" x2="600" y2="110" stroke="#222" stroke-dasharray="4,4" />
          </svg>
          <div class="legend">
            <span><span class="dot pos"></span> positive share</span>
            <span><span class="dot neg"></span> negative share</span>
          </div>
        </div>
      </section>

      <!-- Row: aspect bars + risk terms -->
      <section class="grid-2">
        <div class="panel">
          <h2 class="panel-title">Sentiment by aspect</h2>
          <div v-if="!data.sentiment.by_aspect?.length" class="panel-empty">Not enough data — enrich mentions to populate aspects.</div>
          <div v-else class="aspect-list">
            <div v-for="(a, i) in data.sentiment.by_aspect" :key="i" class="aspect-row">
              <div class="aspect-name">{{ a.aspect }} <span class="aspect-total">({{ a.total }})</span></div>
              <div class="stack-bar">
                <div class="seg pos" :style="{ width: pct(a.positive_share) }"></div>
                <div class="seg neu" :style="{ width: pct(a.neutral_share) }"></div>
                <div class="seg neg" :style="{ width: pct(a.negative_share) }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <h2 class="panel-title">Risk terms</h2>
          <div v-if="!data.keywords.negative_linked?.length" class="panel-empty">No risk terms detected.</div>
          <ul v-else class="risk-list">
            <li v-for="(r, i) in data.keywords.negative_linked.slice(0, 12)" :key="i">
              <span class="risk-term">{{ r.term }}</span>
              <span class="risk-meta">{{ r.negative_count }} negative · {{ pct(r.negative_share) }} share</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- Row: rising terms + impact decomposition -->
      <section class="grid-2">
        <div class="panel">
          <h2 class="panel-title">Rising terms</h2>
          <div v-if="!data.keywords.rising_terms?.length" class="panel-empty">Need a longer time range to detect trends.</div>
          <ul v-else class="rising-list">
            <li v-for="(r, i) in data.keywords.rising_terms.slice(0, 10)" :key="i">
              <span class="rising-term">{{ r.term }}</span>
              <span class="rising-growth">+{{ Math.round(r.growth * 100) }}%</span>
              <span class="rising-detail">{{ r.first_half }} → {{ r.second_half }}</span>
            </li>
          </ul>
        </div>

        <div class="panel">
          <h2 class="panel-title">Impact decomposition</h2>
          <div class="impact-bars">
            <div v-for="(c, key) in impactBars" :key="key" class="impact-row">
              <div class="impact-label">{{ key }}</div>
              <div class="bar-track">
                <div class="bar-fill accent"
                     :style="{ width: c.score == null ? '0%' : `${Math.min(100, c.score)}%`, opacity: c.score == null ? 0.2 : 1 }">
                </div>
              </div>
              <div class="impact-score">{{ c.score == null ? 'n/a' : c.score }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recommendations -->
      <section class="panel">
        <h2 class="panel-title">Recommendations</h2>
        <div v-if="!data.recommendations?.length" class="panel-empty">No actions recommended yet.</div>
        <div v-else class="rec-grid">
          <div v-for="bucket in recBuckets" :key="bucket" class="rec-col">
            <div class="rec-header" :class="bucket">{{ bucket.toUpperCase() }}</div>
            <div v-for="(r, i) in recsByBucket[bucket] || []" :key="i" class="rec-card">
              <div class="rec-title">{{ r.title }}</div>
              <div class="rec-detail">{{ r.detail }}</div>
            </div>
            <div v-if="!(recsByBucket[bucket] || []).length" class="rec-empty">—</div>
          </div>
        </div>
      </section>

      <!-- Asset scores -->
      <section v-if="data.impact?.asset_scores?.length" class="panel">
        <h2 class="panel-title">Creative scoreboard</h2>
        <table class="asset-table">
          <thead>
            <tr>
              <th>Asset</th><th>Type</th><th>Channel</th>
              <th>Mentions</th><th>+ / −</th><th>Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in data.impact.asset_scores" :key="a.asset_id">
              <td class="asset-name">{{ a.filename || a.asset_id.slice(0, 8) }}</td>
              <td>{{ a.asset_type }}</td>
              <td>{{ a.channel || '—' }}</td>
              <td>{{ a.mention_count }}</td>
              <td><span class="pos">{{ a.positive }}</span> / <span class="neg">{{ a.negative }}</span></td>
              <td class="score-cell" :class="scoreClass(a.score)">{{ a.score }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { analyticsApi } from '../api/analytics'

const props = defineProps({ campaignId: { type: String, required: true } })

const data = ref(null)
const loading = ref(true)
const error = ref('')

async function fetchDashboard() {
  loading.value = true
  error.value = ''
  try {
    const res = await analyticsApi.dashboard(props.campaignId)
    data.value = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || e.message
  } finally {
    loading.value = false
  }
}

const maxPhraseCount = computed(() => {
  const list = data.value?.keywords?.top_phrases || []
  return Math.max(1, ...list.map(p => p.count))
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

const recBuckets = ['scale', 'optimize', 'rework', 'investigate']
const recsByBucket = computed(() => {
  const out = {}
  for (const b of recBuckets) out[b] = []
  for (const r of data.value?.recommendations || []) {
    if (out[r.bucket]) out[r.bucket].push(r)
  }
  return out
})

function pct(v) {
  if (v == null) return '—'
  return `${Math.round(v * 100)}%`
}
function barWidth(v, max) {
  return `${Math.max(2, Math.round((v / max) * 100))}%`
}
function trendPoints(field, _color) {
  const days = data.value?.sentiment?.by_day || []
  if (!days.length) return ''
  const W = 600
  const H = 220
  const xStep = days.length > 1 ? W / (days.length - 1) : W
  return days.map((d, i) => {
    const v = d[field] ?? 0
    const x = i * xStep
    const y = H - v * H
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}
function scoreClass(s) {
  if (s >= 70) return 'good'
  if (s >= 40) return 'mid'
  return 'low'
}

onMounted(fetchDashboard)
</script>

<style scoped>
.dash-container { min-height: 100vh; background: #0a0a0a; color: #fff; font-family: 'JetBrains Mono', monospace; }
.navbar { display: flex; justify-content: space-between; padding: 16px 32px; border-bottom: 1px solid #222; }
.nav-brand { font-size: 14px; font-weight: 700; letter-spacing: 4px; }
.nav-links { display: flex; gap: 24px; }
.nav-link { color: #888; text-decoration: none; font-size: 12px; }
.nav-link:hover { color: #fff; }

.state-msg { color: #555; text-align: center; padding: 80px; font-size: 13px; }
.state-msg.error { color: #f44; }

.page-content { padding: 32px; max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.orange-tag { background: #ff6a00; color: #000; font-size: 10px; font-weight: 700; letter-spacing: 2px; padding: 3px 8px; }
.page-title { font-size: 32px; font-weight: 700; margin: 12px 0 4px; }
.page-desc { color: #777; font-size: 13px; margin: 0; }

.cards-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 24px; }
.card { border: 1px solid #222; padding: 16px; }
.card.impact { border-color: #ff6a00; }
.card-label { font-size: 10px; letter-spacing: 1.5px; color: #666; display: flex; gap: 6px; align-items: center; }
.card-value { font-size: 24px; font-weight: 700; margin-top: 8px; }
.card-value.small { font-size: 13px; }
.card-value.positive { color: #0f0; }
.card-value.negative { color: #f44; }
.card-value.accent { color: #ff6a00; font-size: 32px; }
.card-value.risk { color: #f44; }
.badge { font-size: 9px; background: #333; color: #aaa; padding: 1px 5px; border-radius: 2px; letter-spacing: 0.5px; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.panel { border: 1px solid #222; padding: 20px; background: #0c0c0c; margin-bottom: 16px; }
.panel-title { font-size: 12px; font-weight: 700; letter-spacing: 2px; color: #aaa; margin: 0 0 16px; }
.panel-empty { color: #555; font-size: 12px; padding: 20px 0; }

.bar-list, .impact-bars { display: flex; flex-direction: column; gap: 10px; }
.bar-row, .impact-row { display: grid; grid-template-columns: 180px 1fr 50px; gap: 10px; align-items: center; font-size: 12px; }
.bar-label, .impact-label { color: #ccc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { background: #1a1a1a; height: 12px; position: relative; }
.bar-fill { background: #555; height: 100%; transition: width 0.3s; }
.bar-fill.accent { background: #ff6a00; }
.bar-count, .impact-score { color: #ff6a00; text-align: right; font-weight: 700; }

.trend-svg { width: 100%; height: 220px; display: block; }
.legend { display: flex; gap: 20px; font-size: 11px; color: #888; margin-top: 8px; }
.dot { display: inline-block; width: 8px; height: 8px; margin-right: 4px; }
.dot.pos { background: #0f0; } .dot.neg { background: #f44; }

.aspect-list { display: flex; flex-direction: column; gap: 12px; }
.aspect-row { font-size: 12px; }
.aspect-name { color: #ccc; margin-bottom: 4px; text-transform: capitalize; }
.aspect-total { color: #555; }
.stack-bar { display: flex; height: 10px; background: #1a1a1a; }
.stack-bar .seg { height: 100%; }
.stack-bar .seg.pos { background: #0f0; }
.stack-bar .seg.neu { background: #555; }
.stack-bar .seg.neg { background: #f44; }

.risk-list, .rising-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.risk-list li, .rising-list li { display: flex; gap: 12px; font-size: 12px; align-items: center; }
.risk-term, .rising-term { color: #fff; min-width: 120px; }
.risk-meta { color: #666; font-size: 11px; }
.rising-growth { color: #ff6a00; font-weight: 700; }
.rising-detail { color: #555; font-size: 11px; }

.rec-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.rec-col { display: flex; flex-direction: column; gap: 8px; }
.rec-header { font-size: 11px; font-weight: 700; letter-spacing: 2px; padding: 6px 10px; }
.rec-header.scale { background: rgba(0, 255, 0, 0.1); color: #0f0; }
.rec-header.optimize { background: rgba(255, 106, 0, 0.1); color: #ff6a00; }
.rec-header.rework { background: rgba(255, 68, 68, 0.1); color: #f44; }
.rec-header.investigate { background: rgba(120, 120, 255, 0.1); color: #88f; }
.rec-card { border: 1px solid #222; padding: 10px; font-size: 11px; }
.rec-title { color: #fff; margin-bottom: 4px; font-weight: 700; }
.rec-detail { color: #888; line-height: 1.4; }
.rec-empty { color: #333; font-size: 11px; padding: 10px; }

.asset-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.asset-table th, .asset-table td { padding: 8px 12px; border-bottom: 1px solid #1a1a1a; text-align: left; }
.asset-table th { color: #666; font-weight: 400; letter-spacing: 1px; font-size: 10px; }
.asset-table .pos { color: #0f0; }
.asset-table .neg { color: #f44; }
.score-cell { font-weight: 700; }
.score-cell.good { color: #0f0; }
.score-cell.mid { color: #ff6a00; }
.score-cell.low { color: #f44; }
.asset-name { color: #ccc; }
</style>
