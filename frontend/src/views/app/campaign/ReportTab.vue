<template>
  <div class="tab">
    <header class="tab__head">
      <div>
        <span class="tab__eyebrow">REPORT BUILDER</span>
        <h2>Campaign report</h2>
        <p>Generates a narrative report from the latest dashboard snapshot using the configured
        <code>report_writer</code> LLM. Download as markdown or regenerate after new data lands.</p>
      </div>
      <div class="tab__actions">
        <button class="btn btn--primary" :disabled="generating" @click="generate">
          {{ generating ? 'Generating…' : (report ? 'Regenerate' : 'Generate report') }}
        </button>
        <button class="btn btn--ghost" :disabled="!report" @click="downloadMarkdown">Download .md</button>
        <button class="btn btn--ghost" :disabled="exportingMd" @click="exportDashboard">
          {{ exportingMd ? 'Exporting…' : 'Export dashboard snapshot' }}
        </button>
      </div>
    </header>

    <ErrorState
      v-if="error"
      title="Report generation stalled."
      :body="error"
      @retry="generate"
    />

    <div v-if="generating && !report" class="state">
      Asking the LLM to draft the report… this can take 10–30 seconds.
      <LoadingSkeleton height="180px" />
    </div>

    <EmptyState
      v-else-if="!report && !generating && !error"
      title="No report generated yet."
      body="Click 'Generate report' to draft a narrative from the current dashboard snapshot."
    >
      <button class="btn btn--primary" @click="generate">Generate report</button>
    </EmptyState>

    <div v-if="report" class="grid">
      <section class="panel panel--summary">
        <h3>Executive summary</h3>
        <p class="lead">{{ report.sections.executive_summary || '—' }}</p>
        <div class="meta">
          <div class="meta__cell">
            <div class="meta__k">IMPACT</div>
            <div class="meta__v meta__v--accent">{{ report.snapshot?.impact?.score ?? '—' }}</div>
            <div class="meta__s">{{ report.snapshot?.impact?.type || '' }}</div>
          </div>
          <div class="meta__cell">
            <div class="meta__k">MENTIONS</div>
            <div class="meta__v">{{ report.snapshot?.overview?.total_mentions ?? 0 }}</div>
          </div>
          <div class="meta__cell">
            <div class="meta__k">POSITIVE</div>
            <div class="meta__v meta__v--pos">{{ pct(report.snapshot?.sentiment_overall?.positive_share) }}</div>
          </div>
          <div class="meta__cell">
            <div class="meta__k">NEGATIVE</div>
            <div class="meta__v meta__v--neg">{{ pct(report.snapshot?.sentiment_overall?.negative_share) }}</div>
          </div>
        </div>
      </section>

      <section class="panel">
        <h3>Conversation signal</h3>
        <p>{{ report.sections.conversation_signal || '—' }}</p>
      </section>
      <section class="panel">
        <h3>Sentiment read</h3>
        <p>{{ report.sections.sentiment_read || '—' }}</p>
      </section>
      <section class="panel">
        <h3>Creative performance</h3>
        <p>{{ report.sections.creative_performance || '—' }}</p>
      </section>
      <section class="panel">
        <h3>Business outcome</h3>
        <p>{{ report.sections.business_outcome || '—' }}</p>
      </section>

      <section class="panel">
        <h3>Recommendations</h3>
        <ul v-if="report.sections.recommendations?.length" class="recs">
          <li v-for="(r, i) in report.sections.recommendations" :key="i">
            <span class="pri" :class="'pri--' + (r.priority || 'medium').toLowerCase()">
              {{ (r.priority || 'medium').toUpperCase() }}
            </span>
            <span class="rec">
              <strong>{{ r.action }}</strong>
              <span v-if="r.rationale"> — {{ r.rationale }}</span>
            </span>
          </li>
        </ul>
        <div v-else class="panel__empty">No recommendations returned.</div>
      </section>

      <div class="grid-2">
        <section class="panel">
          <h3>Risks</h3>
          <ul v-if="report.sections.risks?.length" class="bullets">
            <li v-for="(r, i) in report.sections.risks" :key="i">{{ r }}</li>
          </ul>
          <div v-else class="panel__empty">None flagged.</div>
        </section>
        <section class="panel">
          <h3>Next steps</h3>
          <ul v-if="report.sections.next_steps?.length" class="bullets">
            <li v-for="(n, i) in report.sections.next_steps" :key="i">{{ n }}</li>
          </ul>
          <div v-else class="panel__empty">None suggested.</div>
        </section>
      </div>

      <details class="drawer">
        <summary>Full markdown</summary>
        <pre>{{ report.markdown }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { analyticsApi } from '@/api/analytics'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const route = useRoute()
const campaignId = computed(() => String(route.params.campaignId))

const report = ref(null)
const generating = ref(false)
const exportingMd = ref(false)
const error = ref('')

async function generate() {
  generating.value = true
  error.value = ''
  try {
    const res = await analyticsApi.generateReport({ campaign_id: campaignId.value })
    report.value = res.data?.data ?? res.data
  } catch (e) {
    error.value = e.response?.data?.error || e.message || 'Report generation failed.'
  } finally {
    generating.value = false
  }
}

function downloadMarkdown() {
  if (!report.value?.markdown) return
  const blob = new Blob([report.value.markdown], { type: 'text/markdown;charset=utf-8' })
  triggerDownload(blob, `campaign-${campaignId.value}-report.md`)
}

async function exportDashboard() {
  exportingMd.value = true
  error.value = ''
  try {
    const res = await analyticsApi.exportDashboardMarkdown(campaignId.value)
    triggerDownload(res.data, `campaign-${campaignId.value}-dashboard.md`)
  } catch (e) {
    error.value = e.response?.data?.error || e.message || 'Export failed.'
  } finally {
    exportingMd.value = false
  }
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function pct(v) {
  if (v == null) return '—'
  return `${Math.round(v * 100)}%`
}
</script>

<style scoped>
.tab { display: flex; flex-direction: column; gap: 20px; padding: 4px 0 40px; }

.tab__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.tab__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.tab__head h2 { font-size: 20px; margin-top: 6px; letter-spacing: -0.01em; }
.tab__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 4px; max-width: 640px; }
.tab__head code { color: var(--co-accent); }
.tab__actions { display: flex; gap: 8px; flex-wrap: wrap; }

.state { display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: var(--co-text-dim); }

.grid { display: flex; flex-direction: column; gap: 14px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 720px) { .grid-2 { grid-template-columns: 1fr; } }

.panel {
  border: 1px solid var(--co-border); background: var(--co-surface); padding: 18px;
}
.panel h3 {
  font-size: 11px; font-weight: 700; letter-spacing: 0.15em;
  color: var(--co-text-dim); margin: 0 0 10px;
}
.panel p { color: var(--co-text); font-size: 13px; line-height: 1.6; margin: 0; }
.panel__empty { color: var(--co-text-mute, #555); font-size: 12px; }

.panel--summary { border-color: var(--co-accent); }
.panel--summary .lead { color: var(--co-text); font-size: 14px; }
.meta { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 18px; }
.meta__cell { border-top: 1px solid var(--co-border); padding-top: 10px; }
.meta__k { font-size: 10px; letter-spacing: 0.12em; color: var(--co-text-dim); }
.meta__v { font-size: 22px; font-weight: 700; margin-top: 4px; }
.meta__v--accent { color: var(--co-accent); }
.meta__v--pos { color: #6efacc; }
.meta__v--neg { color: var(--co-danger, #ff6b6b); }
.meta__s { font-size: 10px; color: var(--co-text-mute, #555); }

.recs { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.recs li { display: flex; gap: 12px; align-items: flex-start; font-size: 13px; }
.pri {
  font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
  padding: 3px 8px; min-width: 64px; text-align: center;
}
.pri--high { background: rgba(255, 68, 68, 0.15); color: var(--co-danger, #ff6b6b); }
.pri--medium { background: rgba(255, 106, 0, 0.15); color: var(--co-accent); }
.pri--low { background: rgba(120, 120, 255, 0.15); color: #88f; }
.rec { color: var(--co-text); line-height: 1.5; }
.rec strong { color: var(--co-text); }

.bullets { color: var(--co-text); font-size: 13px; line-height: 1.7; padding-left: 18px; margin: 0; }
.bullets li { margin-bottom: 4px; }

.drawer { border: 1px solid var(--co-border); padding: 14px; background: var(--co-surface); }
.drawer summary { cursor: pointer; color: var(--co-text-dim); font-size: 12px; letter-spacing: 0.08em; }
.drawer pre {
  color: var(--co-text); font-size: 11px; line-height: 1.5;
  white-space: pre-wrap; margin-top: 12px; max-height: 400px; overflow: auto;
  background: var(--co-bg); padding: 12px;
}

.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius); cursor: pointer;
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }
</style>
