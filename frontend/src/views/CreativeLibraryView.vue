<template>
  <div class="library-container">
    <nav class="navbar">
      <div class="nav-brand">BIGBROTHER</div>
      <div class="nav-links">
        <router-link :to="`/campaign/${campaignId}`" class="nav-link">← Campaign</router-link>
        <router-link :to="`/campaign/${campaignId}/dashboard`" class="nav-link">Dashboard</router-link>
      </div>
    </nav>

    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <span class="orange-tag">CREATIVE LIBRARY</span>
          <h1 class="page-title">Creatives</h1>
          <p class="page-desc">
            Upload images, video, copy. Each asset is OCR'd, transcribed and analyzed
            for hooks, CTA, tone, and offer clarity.
          </p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" :disabled="!unanalyzedIds.length" @click="batchAnalyze">
            Analyze all unprocessed ({{ unanalyzedIds.length }})
          </button>
          <button class="btn-primary" @click="$refs.fileInput.click()">+ Upload</button>
          <input
            ref="fileInput"
            type="file"
            accept=".png,.jpg,.jpeg,.webp,.gif,.mp4,.mov,.mkv,.webm,.txt,.md,.markdown"
            multiple
            hidden
            @change="onFiles"
          />
        </div>
      </div>

      <!-- Filter bar -->
      <div class="filter-bar">
        <span class="filter-label">TYPE:</span>
        <button
          v-for="t in typeFilters"
          :key="t.value"
          class="filter-btn"
          :class="{ active: typeFilter === t.value }"
          @click="typeFilter = t.value"
        >{{ t.label }}</button>

        <span class="filter-label" style="margin-left:24px">STATUS:</span>
        <button
          v-for="s in statusFilters"
          :key="s.value"
          class="filter-btn"
          :class="{ active: statusFilter === s.value }"
          @click="statusFilter = s.value"
        >{{ s.label }}</button>
      </div>

      <!-- Upload progress -->
      <div v-if="uploading.length" class="upload-strip">
        <div v-for="(u, i) in uploading" :key="i" class="upload-row">
          <span class="upload-name">{{ u.name }}</span>
          <span class="upload-state" :class="u.state">{{ u.state }}</span>
        </div>
      </div>

      <div class="library-layout">
        <div class="asset-grid">
          <div v-if="loading" class="state-msg">Loading creatives...</div>
          <div v-else-if="!filteredAssets.length" class="state-msg">
            No creatives match these filters yet.
          </div>

          <div
            v-for="a in filteredAssets"
            :key="a.id"
            class="asset-card"
            :class="{ selected: selected?.id === a.id }"
            @click="selected = a"
          >
            <div class="asset-thumb" :class="a.asset_type">
              <img v-if="a.asset_type === 'image' && a.file_path" :src="thumbUrl(a)" :alt="a.original_filename" />
              <span v-else class="thumb-icon">{{ thumbIcon(a.asset_type) }}</span>
            </div>
            <div class="asset-meta">
              <div class="asset-name">{{ a.original_filename }}</div>
              <div class="asset-row">
                <span class="asset-type">{{ a.asset_type }}</span>
                <span v-if="a.channel" class="asset-channel">{{ a.channel }}</span>
                <span class="asset-status" :class="a.analysis_status">{{ a.analysis_status }}</span>
              </div>
            </div>
          </div>
        </div>

        <aside v-if="selected" class="preview-panel">
          <div class="preview-header">
            <h3>{{ selected.original_filename }}</h3>
            <button class="btn-icon" @click="selected = null" aria-label="Close">×</button>
          </div>

          <div class="preview-body">
            <div v-if="selected.asset_type === 'image'" class="preview-media">
              <img :src="thumbUrl(selected)" :alt="selected.original_filename" />
            </div>

            <div class="preview-row">
              <span class="preview-label">Status</span>
              <span class="preview-value status-badge" :class="selected.analysis_status">{{ selected.analysis_status }}</span>
            </div>
            <div v-if="selected.analysis_error" class="preview-row error">
              <span class="preview-label">Error</span>
              <span class="preview-value">{{ selected.analysis_error }}</span>
            </div>

            <div v-if="selected.cta" class="preview-row">
              <span class="preview-label">CTA</span>
              <span class="preview-value cta">{{ selected.cta }}</span>
            </div>
            <div v-if="selected.emotional_tone" class="preview-row">
              <span class="preview-label">Tone</span>
              <span class="preview-value">{{ selected.emotional_tone }}</span>
            </div>
            <div v-if="selected.offer_clarity_score !== null && selected.offer_clarity_score !== undefined" class="preview-row">
              <span class="preview-label">Clarity</span>
              <span class="preview-value">{{ Number(selected.offer_clarity_score).toFixed(2) }}</span>
            </div>
            <div v-if="selected.detected_hooks?.length" class="preview-row">
              <span class="preview-label">Hooks</span>
              <span class="preview-value tag-row">
                <span v-for="h in selected.detected_hooks" :key="h" class="tag">{{ h }}</span>
              </span>
            </div>
            <div v-if="selected.detected_topics?.length" class="preview-row">
              <span class="preview-label">Topics</span>
              <span class="preview-value tag-row">
                <span v-for="t in selected.detected_topics" :key="t" class="tag">{{ t }}</span>
              </span>
            </div>

            <div v-if="selected.visual_summary" class="preview-block">
              <div class="block-label">Visual summary</div>
              <p>{{ selected.visual_summary }}</p>
            </div>

            <div v-if="selected.ocr_text" class="preview-block">
              <div class="block-label">OCR / source text</div>
              <pre class="block-pre">{{ selected.ocr_text }}</pre>
            </div>

            <div v-if="selected.transcript" class="preview-block">
              <div class="block-label">Transcript</div>
              <pre class="block-pre">{{ selected.transcript }}</pre>
            </div>
          </div>

          <div class="preview-footer">
            <button class="btn-secondary" @click="analyze(selected)" :disabled="selected.analysis_status === 'processing'">
              {{ selected.analysis_status === 'done' ? 'Re-analyze' : 'Analyze' }}
            </button>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({ campaignId: { type: String, required: true } })

const assets = ref([])
const loading = ref(false)
const selected = ref(null)
const uploading = ref([])

const typeFilter = ref('all')
const statusFilter = ref('all')

const typeFilters = [
  { value: 'all', label: 'All' },
  { value: 'image', label: 'Image' },
  { value: 'video', label: 'Video' },
  { value: 'copy', label: 'Copy' },
]
const statusFilters = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'processing', label: 'Processing' },
  { value: 'done', label: 'Done' },
  { value: 'failed', label: 'Failed' },
]

const filteredAssets = computed(() =>
  assets.value.filter((a) =>
    (typeFilter.value === 'all' || a.asset_type === typeFilter.value) &&
    (statusFilter.value === 'all' || a.analysis_status === statusFilter.value)
  )
)

const unanalyzedIds = computed(() =>
  assets.value.filter((a) => a.analysis_status === 'pending' || a.analysis_status === 'failed').map((a) => a.id)
)

const thumbIcon = (type) => ({ video: '▶', copy: '¶', document: '⌘' })[type] || '◇'

const thumbUrl = (asset) => `/api/creatives/${asset.id}/file`

let pollHandle = null

async function fetchAssets() {
  loading.value = true
  try {
    const res = await fetch(`/api/creatives/by-campaign/${props.campaignId}`)
    const json = await res.json()
    if (json.success) {
      assets.value = json.data || []
      if (selected.value) {
        const fresh = assets.value.find((a) => a.id === selected.value.id)
        if (fresh) selected.value = fresh
      }
    }
  } finally {
    loading.value = false
  }
}

async function onFiles(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  for (const file of files) {
    const entry = { name: file.name, state: 'uploading' }
    uploading.value.push(entry)
    try {
      const fd = new FormData()
      fd.append('campaign_id', props.campaignId)
      fd.append('file', file)
      const res = await fetch('/api/creatives/upload', { method: 'POST', body: fd })
      const json = await res.json()
      entry.state = json.success ? 'done' : 'failed'
    } catch (_e) {
      entry.state = 'failed'
    }
  }
  setTimeout(() => {
    uploading.value = uploading.value.filter((u) => u.state === 'uploading')
  }, 2500)
  fetchAssets()
}

async function analyze(asset) {
  await fetch(`/api/creatives/${asset.id}/analyze`, { method: 'POST' })
  asset.analysis_status = 'processing'
}

async function batchAnalyze() {
  if (!unanalyzedIds.value.length) return
  await fetch('/api/creatives/batch-analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asset_ids: unanalyzedIds.value }),
  })
  unanalyzedIds.value.forEach((id) => {
    const a = assets.value.find((x) => x.id === id)
    if (a) a.analysis_status = 'processing'
  })
}

watch(
  () => assets.value.some((a) => a.analysis_status === 'processing'),
  (isProcessing) => {
    if (isProcessing && !pollHandle) {
      pollHandle = setInterval(fetchAssets, 4000)
    } else if (!isProcessing && pollHandle) {
      clearInterval(pollHandle)
      pollHandle = null
    }
  }
)

onMounted(fetchAssets)
onUnmounted(() => {
  if (pollHandle) clearInterval(pollHandle)
})
</script>

<style scoped>
.library-container {
  min-height: 100vh;
  background: var(--bg, #0a0a0a);
  color: var(--text, #f5f5f5);
  font-family: 'JetBrains Mono', 'Inter', system-ui, sans-serif;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  border-bottom: 1px solid var(--border, #222);
}
.nav-brand {
  font-weight: 800;
  letter-spacing: 0.05em;
  color: var(--accent, #ff6a00);
}
.nav-links { display: flex; gap: 18px; }
.nav-link {
  color: var(--text, #f5f5f5);
  text-decoration: none;
  font-size: 13px;
  opacity: 0.85;
}
.nav-link:hover { opacity: 1; color: var(--accent, #ff6a00); }

.page-content { padding: 32px; max-width: 1500px; margin: 0 auto; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 24px;
}
.header-actions { display: flex; gap: 12px; }
.orange-tag {
  display: inline-block;
  background: var(--accent, #ff6a00);
  color: #000;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.page-title {
  font-size: 36px;
  margin: 12px 0 8px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.page-desc { opacity: 0.7; font-size: 14px; max-width: 640px; }

.btn-primary, .btn-secondary {
  border: 1px solid var(--accent, #ff6a00);
  background: var(--accent, #ff6a00);
  color: #000;
  padding: 10px 18px;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  font-size: 12px;
  letter-spacing: 0.05em;
}
.btn-secondary { background: transparent; color: var(--accent, #ff6a00); }
.btn-primary:disabled, .btn-secondary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-icon {
  background: transparent;
  border: none;
  color: var(--text, #f5f5f5);
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.filter-bar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.filter-label { font-size: 11px; opacity: 0.6; letter-spacing: 0.08em; }
.filter-btn {
  background: transparent;
  border: 1px solid var(--border, #222);
  color: var(--text, #f5f5f5);
  padding: 6px 12px;
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
}
.filter-btn.active {
  border-color: var(--accent, #ff6a00);
  color: var(--accent, #ff6a00);
}

.upload-strip {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}
.upload-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 6px 12px;
  border: 1px solid var(--border, #222);
}
.upload-state.uploading { color: #f5d76e; }
.upload-state.done { color: #6efacc; }
.upload-state.failed { color: #ff6b6b; }

.library-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
}
@media (max-width: 1100px) {
  .library-layout { grid-template-columns: 1fr; }
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.state-msg {
  grid-column: 1 / -1;
  padding: 32px;
  text-align: center;
  opacity: 0.6;
}

.asset-card {
  border: 1px solid var(--border, #222);
  background: #111;
  cursor: pointer;
  transition: border-color 0.15s;
  display: flex;
  flex-direction: column;
}
.asset-card:hover, .asset-card.selected {
  border-color: var(--accent, #ff6a00);
}

.asset-thumb {
  aspect-ratio: 16/10;
  background: #181818;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.asset-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.thumb-icon { font-size: 48px; opacity: 0.4; }

.asset-meta { padding: 12px; }
.asset-name {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}
.asset-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  font-size: 10px;
  letter-spacing: 0.05em;
}
.asset-type, .asset-channel, .asset-status {
  padding: 2px 6px;
  border: 1px solid var(--border, #222);
  text-transform: uppercase;
}
.asset-status.pending { color: #888; }
.asset-status.processing { color: #f5d76e; border-color: #f5d76e; }
.asset-status.done { color: #6efacc; border-color: #6efacc; }
.asset-status.failed { color: #ff6b6b; border-color: #ff6b6b; }

.preview-panel {
  border: 1px solid var(--border, #222);
  background: #111;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 200px);
  position: sticky;
  top: 24px;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border, #222);
}
.preview-header h3 {
  font-size: 14px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.preview-media img { width: 100%; display: block; border: 1px solid var(--border, #222); }
.preview-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  padding: 6px 0;
  border-bottom: 1px dashed var(--border, #222);
}
.preview-row.error { color: #ff6b6b; }
.preview-label {
  opacity: 0.6;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 10px;
}
.preview-value { text-align: right; word-break: break-word; }
.preview-value.cta { color: var(--accent, #ff6a00); font-weight: 700; }
.tag-row { display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
.tag {
  padding: 2px 6px;
  border: 1px solid var(--border, #222);
  font-size: 10px;
  text-transform: lowercase;
}
.status-badge.pending { color: #888; }
.status-badge.processing { color: #f5d76e; }
.status-badge.done { color: #6efacc; }
.status-badge.failed { color: #ff6b6b; }

.preview-block {
  margin-top: 8px;
}
.block-label {
  font-size: 10px;
  opacity: 0.6;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}
.preview-block p { font-size: 12px; line-height: 1.5; margin: 0; }
.block-pre {
  background: #0a0a0a;
  padding: 8px;
  font-size: 11px;
  max-height: 180px;
  overflow: auto;
  white-space: pre-wrap;
  margin: 0;
}

.preview-footer {
  padding: 16px;
  border-top: 1px solid var(--border, #222);
}
</style>
