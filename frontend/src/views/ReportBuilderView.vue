<template>
  <div class="rb-container">
    <nav class="navbar">
      <div class="nav-brand">BIGBROTHER</div>
      <div class="nav-links">
        <router-link to="/campaigns" class="nav-link">← Campaigns</router-link>
        <router-link :to="`/campaign/${campaignId}`" class="nav-link">Detail</router-link>
        <router-link :to="`/campaign/${campaignId}/dashboard`" class="nav-link">Dashboard</router-link>
      </div>
    </nav>

    <div class="page-content">
      <header class="page-header">
        <span class="orange-tag">REPORT BUILDER</span>
        <h1 class="page-title">Campaign Report</h1>
        <p class="page-desc">
          Generates a narrative report from the latest dashboard snapshot using the configured
          <code>report_writer</code> LLM. Download as markdown or regenerate after new data lands.
        </p>
      </header>

      <div class="actions-row">
        <button class="btn-primary" :disabled="generating" @click="generate">
          {{ generating ? 'Generating…' : (report ? 'Regenerate' : 'Generate Report') }}
        </button>
        <button class="btn-ghost" :disabled="!report" @click="downloadMarkdown">Download .md</button>
        <button class="btn-ghost" :disabled="exportingMd" @click="exportDashboard">
          {{ exportingMd ? 'Exporting…' : 'Export Dashboard Snapshot' }}
        </button>
      </div>

      <div v-if="error" class="err-msg">{{ error }}</div>

      <div v-if="generating && !report" class="state-msg">
        Asking the LLM to draft the report… this can take 10–30 seconds.
      </div>

      <div v-if="report" class="report-grid">
        <div class="panel summary-panel">
          <h2 class="panel-title">Executive Summary</h2>
          <p class="summary-text">{{ report.sections.executive_summary || '—' }}</p>

          <div class="meta-row">
            <div class="meta-cell">
              <div class="meta-label">IMPACT</div>
              <div class="meta-val accent">{{ report.snapshot?.impact?.score ?? '—' }}</div>
              <div class="meta-sub">{{ report.snapshot?.impact?.type || '' }}</div>
            </div>
            <div class="meta-cell">
              <div class="meta-label">MENTIONS</div>
              <div class="meta-val">{{ report.snapshot?.overview?.total_mentions ?? 0 }}</div>
            </div>
            <div class="meta-cell">
              <div class="meta-label">POSITIVE</div>
              <div class="meta-val pos">{{ pct(report.snapshot?.sentiment_overall?.positive_share) }}</div>
            </div>
            <div class="meta-cell">
              <div class="meta-label">NEGATIVE</div>
              <div class="meta-val neg">{{ pct(report.snapshot?.sentiment_overall?.negative_share) }}</div>
            </div>
          </div>
        </div>

        <div class="panel">
          <h2 class="panel-title">Conversation Signal</h2>
          <p>{{ report.sections.conversation_signal || '—' }}</p>
        </div>

        <div class="panel">
          <h2 class="panel-title">Sentiment Read</h2>
          <p>{{ report.sections.sentiment_read || '—' }}</p>
        </div>

        <div class="panel">
          <h2 class="panel-title">Creative Performance</h2>
          <p>{{ report.sections.creative_performance || '—' }}</p>
        </div>

        <div class="panel">
          <h2 class="panel-title">Business Outcome</h2>
          <p>{{ report.sections.business_outcome || '—' }}</p>
        </div>

        <div class="panel">
          <h2 class="panel-title">Recommendations</h2>
          <ul v-if="report.sections.recommendations?.length" class="rec-list">
            <li v-for="(r, i) in report.sections.recommendations" :key="i">
              <span class="rec-pri" :class="(r.priority || 'medium').toLowerCase()">
                {{ (r.priority || 'medium').toUpperCase() }}
              </span>
              <span class="rec-body">
                <strong>{{ r.action }}</strong>
                <span v-if="r.rationale"> — {{ r.rationale }}</span>
              </span>
            </li>
          </ul>
          <div v-else class="panel-empty">No recommendations returned.</div>
        </div>

        <div class="grid-2">
          <div class="panel">
            <h2 class="panel-title">Risks</h2>
            <ul v-if="report.sections.risks?.length" class="bullet-list">
              <li v-for="(r, i) in report.sections.risks" :key="i">{{ r }}</li>
            </ul>
            <div v-else class="panel-empty">None flagged.</div>
          </div>
          <div class="panel">
            <h2 class="panel-title">Next Steps</h2>
            <ul v-if="report.sections.next_steps?.length" class="bullet-list">
              <li v-for="(n, i) in report.sections.next_steps" :key="i">{{ n }}</li>
            </ul>
            <div v-else class="panel-empty">None suggested.</div>
          </div>
        </div>

        <details class="markdown-drawer">
          <summary>Full markdown</summary>
          <pre class="md-pre">{{ report.markdown }}</pre>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { analyticsApi } from '../api/analytics'

const props = defineProps({ campaignId: { type: String, required: true } })

const report = ref(null)
const generating = ref(false)
const exportingMd = ref(false)
const error = ref('')

async function generate() {
  generating.value = true
  error.value = ''
  try {
    const res = await analyticsApi.generateReport({ campaign_id: props.campaignId })
    report.value = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || e.message
  } finally {
    generating.value = false
  }
}

function downloadMarkdown() {
  if (!report.value?.markdown) return
  const blob = new Blob([report.value.markdown], { type: 'text/markdown;charset=utf-8' })
  triggerDownload(blob, `campaign-${props.campaignId}-report.md`)
}

async function exportDashboard() {
  exportingMd.value = true
  error.value = ''
  try {
    const res = await analyticsApi.exportDashboardMarkdown(props.campaignId)
    triggerDownload(res.data, `campaign-${props.campaignId}-dashboard.md`)
  } catch (e) {
    error.value = e.response?.data?.error || e.message
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
.rb-container { min-height: 100vh; background: #0a0a0a; color: #fff; font-family: 'JetBrains Mono', monospace; }
.navbar { display: flex; justify-content: space-between; padding: 16px 32px; border-bottom: 1px solid #222; }
.nav-brand { font-size: 14px; font-weight: 700; letter-spacing: 4px; }
.nav-links { display: flex; gap: 24px; }
.nav-link { color: #888; text-decoration: none; font-size: 12px; }
.nav-link:hover { color: #fff; }

.page-content { padding: 32px; max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.orange-tag { background: #ff6a00; color: #000; font-size: 10px; font-weight: 700; letter-spacing: 2px; padding: 3px 8px; }
.page-title { font-size: 32px; font-weight: 700; margin: 12px 0 4px; }
.page-desc { color: #777; font-size: 13px; margin: 0; }
.page-desc code { color: #ff6a00; }

.actions-row { display: flex; gap: 12px; margin-bottom: 20px; }
.btn-primary { background: #ff6a00; color: #000; border: none; padding: 10px 20px; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; letter-spacing: 1px; }
.btn-primary:disabled { opacity: 0.4; cursor: default; }
.btn-ghost { background: transparent; color: #ccc; border: 1px solid #333; padding: 10px 20px; font-family: inherit; font-size: 12px; cursor: pointer; }
.btn-ghost:hover { border-color: #fff; }
.btn-ghost:disabled { opacity: 0.4; cursor: default; }

.err-msg { color: #f44; font-size: 12px; margin-bottom: 16px; }
.state-msg { color: #666; font-size: 13px; padding: 40px 0; }

.report-grid { display: flex; flex-direction: column; gap: 16px; }
.panel { border: 1px solid #222; padding: 20px; background: #0c0c0c; }
.panel-title { font-size: 12px; font-weight: 700; letter-spacing: 2px; color: #aaa; margin: 0 0 12px; }
.panel p { color: #ccc; font-size: 13px; line-height: 1.6; margin: 0; }
.panel-empty { color: #555; font-size: 12px; }

.summary-panel { border-color: #ff6a00; }
.summary-text { color: #fff !important; font-size: 14px !important; }
.meta-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 20px; }
.meta-cell { border-top: 1px solid #222; padding-top: 10px; }
.meta-label { font-size: 10px; letter-spacing: 1.5px; color: #666; }
.meta-val { font-size: 24px; font-weight: 700; margin-top: 4px; }
.meta-val.accent { color: #ff6a00; }
.meta-val.pos { color: #0f0; }
.meta-val.neg { color: #f44; }
.meta-sub { font-size: 10px; color: #555; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.rec-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.rec-list li { display: flex; gap: 12px; align-items: flex-start; font-size: 13px; }
.rec-pri { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; padding: 2px 8px; min-width: 60px; text-align: center; }
.rec-pri.high { background: rgba(255, 68, 68, 0.15); color: #f44; }
.rec-pri.medium { background: rgba(255, 106, 0, 0.15); color: #ff6a00; }
.rec-pri.low { background: rgba(120, 120, 255, 0.15); color: #88f; }
.rec-body { color: #ccc; line-height: 1.5; }
.rec-body strong { color: #fff; }

.bullet-list { color: #ccc; font-size: 13px; line-height: 1.7; padding-left: 18px; margin: 0; }
.bullet-list li { margin-bottom: 4px; }

.markdown-drawer { border: 1px solid #222; padding: 14px; background: #0c0c0c; }
.markdown-drawer summary { cursor: pointer; color: #aaa; font-size: 12px; letter-spacing: 1px; }
.md-pre { color: #ddd; font-size: 11px; line-height: 1.5; white-space: pre-wrap; margin-top: 12px; max-height: 400px; overflow: auto; background: #050505; padding: 12px; }
</style>
