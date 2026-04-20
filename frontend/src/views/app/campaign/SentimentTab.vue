<template>
  <div class="tab">
    <header class="tab__head">
      <div>
        <span class="tab__eyebrow">SENTIMENT DEEP-DIVE</span>
        <h2>Sentiment</h2>
        <p>Day-over-day trend, aspect breakdown, and emotion split across mentions.</p>
      </div>
    </header>

    <div v-if="loading && !data" class="skeletons">
      <LoadingSkeleton v-for="i in 4" :key="i" height="120px" />
    </div>

    <ErrorState
      v-else-if="error"
      title="Couldn't load sentiment."
      :body="String(error?.message || error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!data || !hasSentiment"
      title="Not enough mentions to score sentiment."
      body="We need at least a handful of mentions spanning multiple days to produce aspect breakdowns."
    >
      <router-link :to="{ name: 'CampaignMentions' }" class="btn btn--primary">Import mentions</router-link>
    </EmptyState>

    <div v-else class="grid">
      <section class="panel panel--wide">
        <header class="panel__head">
          <h3>Sentiment trend</h3>
          <span class="panel__sub">{{ days.length }} day{{ days.length === 1 ? '' : 's' }}</span>
        </header>
        <svg class="trend" viewBox="0 0 600 220" preserveAspectRatio="none">
          <line x1="0" y1="110" x2="600" y2="110" stroke="var(--co-border)" stroke-dasharray="4,4" />
          <polyline :points="trendPoints('positive_share')" fill="none" stroke="#3ecf8e" stroke-width="2" />
          <polyline :points="trendPoints('neutral_share')"  fill="none" stroke="var(--co-border-2)" stroke-width="2" />
          <polyline :points="trendPoints('negative_share')" fill="none" stroke="#ff5469" stroke-width="2" />
        </svg>
        <div class="legend">
          <span><i class="dot" style="background:#3ecf8e"></i> positive</span>
          <span><i class="dot" style="background:var(--co-border-2)"></i> neutral</span>
          <span><i class="dot" style="background:#ff5469"></i> negative</span>
        </div>
      </section>

      <section class="panel">
        <header class="panel__head">
          <h3>Overall mix</h3>
        </header>
        <div class="mix">
          <div class="mix__row">
            <span>Positive</span>
            <strong class="mix__pos">{{ pct(overall.positive_share) }}</strong>
          </div>
          <div class="mix__row">
            <span>Neutral</span>
            <strong>{{ pct(overall.neutral_share) }}</strong>
          </div>
          <div class="mix__row">
            <span>Negative</span>
            <strong class="mix__neg">{{ pct(overall.negative_share) }}</strong>
          </div>
          <div class="mix__bar">
            <span class="seg seg--pos" :style="{ width: pct(overall.positive_share) }"></span>
            <span class="seg seg--neu" :style="{ width: pct(overall.neutral_share) }"></span>
            <span class="seg seg--neg" :style="{ width: pct(overall.negative_share) }"></span>
          </div>
        </div>
      </section>

      <section class="panel">
        <header class="panel__head">
          <h3>Emotion split</h3>
        </header>
        <div v-if="!emotions.length" class="panel__empty">No emotion labels detected.</div>
        <ul v-else class="emotions">
          <li v-for="(e, i) in emotions" :key="i">
            <span class="emotions__name">{{ e.emotion }}</span>
            <div class="emotions__bar"><span :style="{ width: pct(e.share) }"></span></div>
            <span class="emotions__count">{{ e.count }}</span>
          </li>
        </ul>
      </section>

      <section class="panel panel--wide">
        <header class="panel__head">
          <h3>By aspect</h3>
          <span class="panel__sub">{{ aspects.length }} aspects</span>
        </header>
        <div v-if="!aspects.length" class="panel__empty">Enrich mentions to populate aspects.</div>
        <ul v-else class="aspects">
          <li v-for="(a, i) in aspects" :key="i">
            <div class="aspects__head">
              <span class="aspects__name">{{ a.aspect }}</span>
              <span class="aspects__total">{{ a.total }} mentions</span>
            </div>
            <div class="aspects__bar">
              <span class="seg seg--pos" :style="{ width: pct(a.positive_share) }"></span>
              <span class="seg seg--neu" :style="{ width: pct(a.neutral_share) }"></span>
              <span class="seg seg--neg" :style="{ width: pct(a.negative_share) }"></span>
            </div>
            <div class="aspects__meta">
              <span class="mix__pos">{{ pct(a.positive_share) }}</span>
              <span>{{ pct(a.neutral_share) }}</span>
              <span class="mix__neg">{{ pct(a.negative_share) }}</span>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const route = useRoute()
const analytics = useAnalyticsStore()

const campaignId = computed(() => String(route.params.campaignId))
const data = computed(() => analytics.dashboardByCampaign[campaignId.value])
const loading = computed(() => analytics.loading)
const error = computed(() => analytics.error)

const sentiment = computed(() => data.value?.sentiment || {})
const days = computed(() => sentiment.value.by_day || [])
const aspects = computed(() => sentiment.value.by_aspect || [])
const emotions = computed(() => sentiment.value.by_emotion || [])
const overall = computed(() => sentiment.value.overall || data.value?.overview || {})
const hasSentiment = computed(() => days.value.length || aspects.value.length || emotions.value.length)

function pct(v) { return v == null ? '—' : `${Math.round(v * 100)}%` }
function trendPoints(field) {
  const list = days.value
  if (!list.length) return ''
  const W = 600, H = 220
  const xStep = list.length > 1 ? W / (list.length - 1) : W
  return list.map((d, i) => {
    const v = d[field] ?? 0
    return `${(i * xStep).toFixed(1)},${(H - v * H).toFixed(1)}`
  }).join(' ')
}

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

.skeletons { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }

.panel {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.panel--wide { grid-column: 1 / -1; }
.panel__head { display: flex; justify-content: space-between; align-items: center; }
.panel__head h3 { font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--co-text-dim); }
.panel__sub { font-size: 11px; color: var(--co-text-mute, #666); }
.panel__empty { font-size: 12px; color: var(--co-text-mute, #666); padding: 24px 0; text-align: center; }

.trend { width: 100%; height: 220px; }
.legend { display: flex; gap: 14px; font-size: 11px; color: var(--co-text-dim); }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }

.mix { display: flex; flex-direction: column; gap: 8px; font-size: 12px; }
.mix__row { display: flex; justify-content: space-between; align-items: center; }
.mix__row strong { font-size: 16px; }
.mix__pos { color: #3ecf8e; }
.mix__neg { color: #ff5469; }
.mix__bar { display: flex; height: 10px; background: var(--co-bg); margin-top: 6px; }
.seg { display: block; height: 100%; }
.seg--pos { background: #3ecf8e; }
.seg--neu { background: var(--co-border-2); }
.seg--neg { background: #ff5469; }

.emotions { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; font-size: 12px; }
.emotions li { display: grid; grid-template-columns: 100px 1fr 40px; gap: 10px; align-items: center; }
.emotions__name { color: var(--co-text); text-transform: lowercase; }
.emotions__bar { background: var(--co-bg); height: 6px; }
.emotions__bar span { display: block; height: 100%; background: var(--co-accent); }
.emotions__count { font-size: 11px; color: var(--co-text-dim); text-align: right; }

.aspects { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 14px; }
.aspects__head { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
.aspects__name { color: var(--co-text); text-transform: capitalize; }
.aspects__total { color: var(--co-text-dim); font-size: 11px; }
.aspects__bar { display: flex; height: 8px; background: var(--co-bg); }
.aspects__meta { display: flex; justify-content: space-between; font-size: 10px; margin-top: 4px; }

.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius);
}
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
</style>
