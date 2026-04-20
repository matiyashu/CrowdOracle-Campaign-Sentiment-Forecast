<template>
  <div class="tab">
    <header class="tab__head">
      <div>
        <span class="tab__eyebrow">MENTIONS · KEYWORDS</span>
        <h2>Mentions</h2>
        <p>What audiences are saying — pulled from uploaded mention streams.</p>
      </div>
      <button class="btn btn--primary" @click="pickFile">Import mentions</button>
      <input ref="fileInput" type="file" accept=".csv,.json" hidden @change="onFile" />
    </header>

    <div v-if="uploadMsg" class="banner" :class="'banner--' + uploadMsg.state">{{ uploadMsg.text }}</div>

    <div v-if="loading && !data" class="skeletons">
      <LoadingSkeleton v-for="i in 4" :key="i" height="80px" />
    </div>

    <ErrorState
      v-else-if="error"
      title="Couldn't load mentions."
      :body="String(error?.message || error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!data || !hasKeywords"
      title="No mentions linked."
      body="Import a CSV from your listening tool or paste a sample."
    >
      <button class="btn btn--primary" @click="pickFile">Import mentions</button>
    </EmptyState>

    <div v-else class="layout">
      <section class="panel">
        <header class="panel__head">
          <h3>Top phrases</h3>
          <span class="panel__sub">{{ phrases.length }} terms</span>
        </header>
        <div v-if="!phrases.length" class="panel__empty">No phrases extracted yet.</div>
        <ul v-else class="phrases">
          <li v-for="(p, i) in phrases" :key="i">
            <span class="phrases__term">{{ p.phrase }}</span>
            <div class="phrases__bar"><span :style="{ width: barW(p.count, maxPhrase) }"></span></div>
            <span class="phrases__count">{{ p.count }}</span>
          </li>
        </ul>
      </section>

      <section class="panel">
        <header class="panel__head">
          <h3>Rising terms</h3>
          <span class="panel__sub">growth vs. prior window</span>
        </header>
        <div v-if="!rising.length" class="panel__empty">Need a longer time range to detect trends.</div>
        <ul v-else class="rising">
          <li v-for="(r, i) in rising" :key="i">
            <span class="rising__term">{{ r.term }}</span>
            <span class="rising__growth">+{{ Math.round(r.growth * 100) }}%</span>
            <span class="rising__detail">{{ r.first_half }} → {{ r.second_half }}</span>
          </li>
        </ul>
      </section>

      <section class="panel panel--wide">
        <header class="panel__head">
          <h3>Risk terms</h3>
          <span class="panel__sub">Phrases that cluster with negative sentiment</span>
        </header>
        <div v-if="!risks.length" class="panel__empty">No risk terms detected.</div>
        <ul v-else class="risks">
          <li v-for="(r, i) in risks" :key="i">
            <span class="risks__term">{{ r.term }}</span>
            <span class="risks__meta">
              {{ r.negative_count }} negative · {{ pct(r.negative_share) }} share
            </span>
          </li>
        </ul>
      </section>
    </div>
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

const keywords = computed(() => data.value?.keywords || {})
const phrases = computed(() => (keywords.value.top_phrases || []).slice(0, 20))
const rising = computed(() => (keywords.value.rising_terms || []).slice(0, 15))
const risks = computed(() => (keywords.value.negative_linked || []).slice(0, 20))
const hasKeywords = computed(() => phrases.value.length || rising.value.length || risks.value.length)
const maxPhrase = computed(() => Math.max(1, ...(phrases.value.map((p) => p.count))))

const fileInput = ref(null)
const uploadMsg = ref(null)

function pickFile() { fileInput.value?.click() }
async function onFile(ev) {
  const file = ev.target.files?.[0]
  ev.target.value = ''
  if (!file) return
  uploadMsg.value = { state: 'info', text: `Uploading ${file.name}…` }
  try {
    await analyticsApi.uploadMentions(campaignId.value, file)
    uploadMsg.value = { state: 'ok', text: 'Mentions imported.' }
    reload()
  } catch (e) {
    uploadMsg.value = { state: 'err', text: e?.response?.data?.error || e.message || 'Upload failed.' }
  }
  setTimeout(() => (uploadMsg.value = null), 4000)
}

function pct(v) { return v == null ? '—' : `${Math.round(v * 100)}%` }
function barW(v, max) { return `${Math.max(2, Math.round((v / max) * 100))}%` }

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
.banner--info { color: var(--co-text-dim); }

.skeletons { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

.layout { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 960px) { .layout { grid-template-columns: 1fr; } }

.panel {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.panel--wide { grid-column: 1 / -1; }
.panel__head { display: flex; justify-content: space-between; align-items: center; }
.panel__head h3 { font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--co-text-dim); }
.panel__sub { font-size: 11px; color: var(--co-text-mute, #666); }
.panel__empty { font-size: 12px; color: var(--co-text-mute, #666); padding: 24px 0; text-align: center; }

.phrases { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; font-size: 12px; }
.phrases li { display: grid; grid-template-columns: 1fr 80px 30px; gap: 8px; align-items: center; }
.phrases__bar { background: var(--co-bg); height: 6px; }
.phrases__bar span { display: block; height: 100%; background: var(--co-accent); }
.phrases__count { font-size: 11px; color: var(--co-text-dim); text-align: right; }

.rising { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; font-size: 12px; }
.rising li { display: grid; grid-template-columns: 1fr auto auto; gap: 12px; align-items: center; padding: 6px 0; border-bottom: 1px dashed var(--co-border); }
.rising__term { color: var(--co-text); }
.rising__growth { color: var(--co-accent); font-weight: 700; }
.rising__detail { color: var(--co-text-dim); font-size: 11px; }

.risks { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 10px; font-size: 12px; }
.risks li {
  background: var(--co-bg); padding: 10px; border: 1px solid var(--co-border);
  display: flex; flex-direction: column; gap: 4px;
}
.risks__term { color: var(--co-text); font-weight: 700; }
.risks__meta { color: var(--co-text-dim); font-size: 11px; }

.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
</style>
