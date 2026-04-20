<template>
  <div class="tab">
    <header class="tab__head">
      <div>
        <span class="tab__eyebrow">CREATIVE LIBRARY</span>
        <h2>Creatives</h2>
        <p>Upload images, video, copy. Each asset is OCR'd, transcribed and analyzed
        for hooks, CTA, tone, and offer clarity.</p>
      </div>
      <div class="tab__actions">
        <button
          class="btn btn--ghost"
          :disabled="!unanalyzedIds.length"
          @click="onBatchAnalyze"
        >Analyze all unprocessed ({{ unanalyzedIds.length }})</button>
        <button class="btn btn--primary" @click="pickFiles">+ Upload</button>
        <input
          ref="fileInput"
          type="file"
          accept=".png,.jpg,.jpeg,.webp,.gif,.mp4,.mov,.mkv,.webm,.txt,.md,.markdown"
          multiple
          hidden
          @change="onFiles"
        />
      </div>
    </header>

    <div class="filters">
      <span class="filters__label">TYPE</span>
      <button
        v-for="t in typeFilters"
        :key="t.value"
        class="chip"
        :class="{ 'chip--on': typeFilter === t.value }"
        @click="typeFilter = t.value"
      >{{ t.label }}</button>

      <span class="filters__label filters__label--gap">STATUS</span>
      <button
        v-for="s in statusFilters"
        :key="s.value"
        class="chip"
        :class="{ 'chip--on': statusFilter === s.value }"
        @click="statusFilter = s.value"
      >{{ s.label }}</button>
    </div>

    <div v-if="uploading.length" class="upstrip">
      <div v-for="(u, i) in uploading" :key="i" class="upstrip__row">
        <span>{{ u.name }}</span>
        <span class="upstrip__state" :class="'upstrip__state--' + u.state">{{ u.state }}</span>
      </div>
    </div>

    <div v-if="creatives.loading && !assets.length" class="skeletons">
      <LoadingSkeleton v-for="i in 4" :key="i" height="160px" />
    </div>

    <ErrorState
      v-else-if="creatives.error"
      title="Couldn't load creatives."
      :body="String(creatives.error?.message || creatives.error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!assets.length"
      title="Nothing to analyze yet."
      body="Drop images, videos, or copy here to get hook / OCR / transcript breakdowns."
    >
      <button class="btn btn--primary" @click="pickFiles">Upload creatives</button>
    </EmptyState>

    <div v-else class="layout">
      <div class="grid">
        <div v-if="!filteredAssets.length" class="grid__empty">
          No creatives match these filters.
        </div>
        <article
          v-for="a in filteredAssets"
          :key="a.id"
          class="card"
          :class="{ 'card--on': selected?.id === a.id }"
          @click="selected = a"
        >
          <div class="card__thumb">
            <img v-if="a.asset_type === 'image' && a.file_path" :src="thumbUrl(a)" :alt="a.original_filename" />
            <span v-else class="card__icon">{{ thumbIcon(a.asset_type) }}</span>
          </div>
          <div class="card__meta">
            <div class="card__name" :title="a.original_filename">{{ a.original_filename }}</div>
            <div class="card__row">
              <span class="pill">{{ a.asset_type }}</span>
              <span v-if="a.channel" class="pill">{{ a.channel }}</span>
              <span class="pill" :class="'pill--' + a.analysis_status">{{ a.analysis_status }}</span>
            </div>
          </div>
        </article>
      </div>

      <aside v-if="selected" class="preview">
        <div class="preview__head">
          <h3 :title="selected.original_filename">{{ selected.original_filename }}</h3>
          <button class="btn-x" @click="selected = null" aria-label="Close">×</button>
        </div>

        <div class="preview__body">
          <div v-if="selected.asset_type === 'image'" class="preview__media">
            <img :src="thumbUrl(selected)" :alt="selected.original_filename" />
          </div>

          <div class="kv">
            <span class="kv__k">Status</span>
            <span class="pill" :class="'pill--' + selected.analysis_status">{{ selected.analysis_status }}</span>
          </div>
          <div v-if="selected.analysis_error" class="kv kv--error">
            <span class="kv__k">Error</span>
            <span>{{ selected.analysis_error }}</span>
          </div>
          <div v-if="selected.cta" class="kv">
            <span class="kv__k">CTA</span>
            <span class="kv__cta">{{ selected.cta }}</span>
          </div>
          <div v-if="selected.emotional_tone" class="kv">
            <span class="kv__k">Tone</span>
            <span>{{ selected.emotional_tone }}</span>
          </div>
          <div v-if="selected.offer_clarity_score != null" class="kv">
            <span class="kv__k">Clarity</span>
            <span>{{ Number(selected.offer_clarity_score).toFixed(2) }}</span>
          </div>
          <div v-if="selected.detected_hooks?.length" class="kv">
            <span class="kv__k">Hooks</span>
            <span class="tagrow">
              <span v-for="h in selected.detected_hooks" :key="h" class="tag">{{ h }}</span>
            </span>
          </div>
          <div v-if="selected.detected_topics?.length" class="kv">
            <span class="kv__k">Topics</span>
            <span class="tagrow">
              <span v-for="t in selected.detected_topics" :key="t" class="tag">{{ t }}</span>
            </span>
          </div>

          <div v-if="selected.visual_summary" class="block">
            <div class="block__label">Visual summary</div>
            <p>{{ selected.visual_summary }}</p>
          </div>
          <div v-if="selected.ocr_text" class="block">
            <div class="block__label">OCR / source text</div>
            <pre>{{ selected.ocr_text }}</pre>
          </div>
          <div v-if="selected.transcript" class="block">
            <div class="block__label">Transcript</div>
            <pre>{{ selected.transcript }}</pre>
          </div>
        </div>

        <footer class="preview__foot">
          <button
            class="btn btn--ghost"
            :disabled="selected.analysis_status === 'processing'"
            @click="onAnalyze(selected)"
          >{{ selected.analysis_status === 'done' ? 'Re-analyze' : 'Analyze' }}</button>
        </footer>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCreativesStore } from '@/stores/creatives'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

const route = useRoute()
const campaignId = computed(() => String(route.params.campaignId))
const creatives = useCreativesStore()

const fileInput = ref(null)
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

const assets = computed(() => creatives.byCampaign[campaignId.value] || [])

const filteredAssets = computed(() =>
  assets.value.filter((a) =>
    (typeFilter.value === 'all' || a.asset_type === typeFilter.value) &&
    (statusFilter.value === 'all' || a.analysis_status === statusFilter.value)
  )
)

const unanalyzedIds = computed(() =>
  assets.value
    .filter((a) => a.analysis_status === 'pending' || a.analysis_status === 'failed')
    .map((a) => a.id)
)

const thumbIcon = (type) => ({ video: '▶', copy: '¶', document: '⌘' }[type] || '◇')
const thumbUrl = (a) => `/api/creatives/${a.id}/file`

async function reload() {
  await creatives.loadByCampaign(campaignId.value)
  if (selected.value) {
    const fresh = assets.value.find((a) => a.id === selected.value.id)
    if (fresh) selected.value = fresh
  }
}

function pickFiles() { fileInput.value?.click() }

async function onFiles(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  for (const file of files) {
    const entry = { name: file.name, state: 'uploading' }
    uploading.value.push(entry)
    try {
      await creatives.upload(campaignId.value, file)
      entry.state = 'done'
    } catch {
      entry.state = 'failed'
    }
  }
  setTimeout(() => {
    uploading.value = uploading.value.filter((u) => u.state === 'uploading')
  }, 2500)
  reload()
}

async function onAnalyze(asset) {
  await creatives.analyze(asset.id)
  asset.analysis_status = 'processing'
}

async function onBatchAnalyze() {
  if (!unanalyzedIds.value.length) return
  const ids = [...unanalyzedIds.value]
  await creatives.batchAnalyze(ids)
  ids.forEach((id) => {
    const a = assets.value.find((x) => x.id === id)
    if (a) a.analysis_status = 'processing'
  })
}

let pollHandle = null
watch(
  () => assets.value.some((a) => a.analysis_status === 'processing'),
  (isProcessing) => {
    if (isProcessing && !pollHandle) pollHandle = setInterval(reload, 4000)
    else if (!isProcessing && pollHandle) { clearInterval(pollHandle); pollHandle = null }
  }
)

watch(campaignId, (id) => id && reload())
onMounted(reload)
onUnmounted(() => { if (pollHandle) clearInterval(pollHandle) })
</script>

<style scoped>
.tab { display: flex; flex-direction: column; gap: 20px; padding: 4px 0 40px; }

.tab__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.tab__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.tab__head h2 { font-size: 20px; margin-top: 6px; letter-spacing: -0.01em; }
.tab__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 4px; max-width: 620px; }
.tab__actions { display: flex; gap: 8px; flex-wrap: wrap; }

.filters { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.filters__label { font-size: 10px; color: var(--co-text-dim); letter-spacing: 0.15em; margin-right: 4px; }
.filters__label--gap { margin-left: 12px; }
.chip {
  background: transparent; border: 1px solid var(--co-border-2);
  color: var(--co-text-dim); font-family: var(--co-font-mono);
  font-size: 11px; padding: 5px 10px; cursor: pointer; border-radius: var(--co-radius);
}
.chip:hover { color: var(--co-text); }
.chip--on { color: var(--co-accent); border-color: var(--co-accent); }

.upstrip { display: flex; flex-direction: column; gap: 4px; }
.upstrip__row {
  display: flex; justify-content: space-between;
  font-size: 12px; padding: 6px 12px;
  border: 1px solid var(--co-border); background: var(--co-surface);
}
.upstrip__state--uploading { color: #f5d76e; }
.upstrip__state--done { color: var(--co-accent-2, #6efacc); }
.upstrip__state--failed { color: var(--co-danger, #ff6b6b); }

.skeletons { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }

.layout { display: grid; grid-template-columns: 1fr 380px; gap: 20px; }
@media (max-width: 1100px) { .layout { grid-template-columns: 1fr; } }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.grid__empty { grid-column: 1 / -1; padding: 32px; text-align: center; color: var(--co-text-dim); font-size: 12px; }

.card {
  border: 1px solid var(--co-border); background: var(--co-surface);
  cursor: pointer; display: flex; flex-direction: column;
  transition: border-color 0.15s;
}
.card:hover, .card--on { border-color: var(--co-accent); }
.card__thumb {
  aspect-ratio: 16/10; background: var(--co-bg);
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.card__thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.card__icon { font-size: 44px; color: var(--co-text-mute, #666); }
.card__meta { padding: 10px 12px; }
.card__name {
  font-size: 12px; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; margin-bottom: 6px;
}
.card__row { display: flex; gap: 6px; flex-wrap: wrap; }

.pill {
  padding: 2px 6px; border: 1px solid var(--co-border-2);
  font-size: 10px; letter-spacing: 0.05em; text-transform: uppercase;
  color: var(--co-text-dim);
}
.pill--processing { color: #f5d76e; border-color: #f5d76e; }
.pill--done { color: var(--co-accent-2, #6efacc); border-color: var(--co-accent-2, #6efacc); }
.pill--failed { color: var(--co-danger, #ff6b6b); border-color: var(--co-danger, #ff6b6b); }

.preview {
  border: 1px solid var(--co-border); background: var(--co-surface);
  display: flex; flex-direction: column;
  max-height: calc(100vh - 220px); position: sticky; top: 24px;
}
.preview__head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px; border-bottom: 1px solid var(--co-border);
}
.preview__head h3 {
  font-size: 13px; margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.btn-x {
  background: transparent; border: none; color: var(--co-text);
  font-size: 22px; cursor: pointer; line-height: 1;
}
.preview__body {
  flex: 1; overflow-y: auto; padding: 14px 16px;
  display: flex; flex-direction: column; gap: 10px;
}
.preview__media img {
  width: 100%; display: block;
  border: 1px solid var(--co-border);
}
.kv {
  display: flex; justify-content: space-between; gap: 12px;
  font-size: 12px; padding: 6px 0;
  border-bottom: 1px dashed var(--co-border);
}
.kv--error { color: var(--co-danger, #ff6b6b); }
.kv__k {
  color: var(--co-text-dim); text-transform: uppercase;
  letter-spacing: 0.05em; font-size: 10px;
}
.kv__cta { color: var(--co-accent); font-weight: 700; }
.tagrow { display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
.tag {
  padding: 2px 6px; border: 1px solid var(--co-border-2);
  font-size: 10px; text-transform: lowercase;
}
.block { margin-top: 6px; }
.block__label {
  font-size: 10px; color: var(--co-text-dim);
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;
}
.block p { font-size: 12px; line-height: 1.5; margin: 0; color: var(--co-text); }
.block pre {
  background: var(--co-bg); padding: 8px;
  font-size: 11px; max-height: 180px; overflow: auto;
  white-space: pre-wrap; margin: 0;
}
.preview__foot { padding: 14px 16px; border-top: 1px solid var(--co-border); }

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
