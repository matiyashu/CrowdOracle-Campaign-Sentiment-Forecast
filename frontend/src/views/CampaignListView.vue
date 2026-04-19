<template>
  <div class="campaigns-container">
    <nav class="navbar">
      <div class="nav-brand">BIGBROTHER</div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">← Simulation</router-link>
        <router-link to="/settings/providers" class="nav-link">Providers</router-link>
      </div>
    </nav>

    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <span class="orange-tag">CAMPAIGN INTELLIGENCE</span>
          <h1 class="page-title">Campaigns</h1>
          <p class="page-desc">Manage campaign workspaces, upload creatives, and generate impact reports.</p>
        </div>
        <button class="btn-primary" @click="showCreate = true">+ New Campaign</button>
      </div>

      <!-- Filter bar -->
      <div class="filter-bar">
        <span class="filter-label">STATUS:</span>
        <button
          v-for="s in statuses"
          :key="s.value"
          class="filter-btn"
          :class="{ active: statusFilter === s.value }"
          @click="statusFilter = s.value"
        >{{ s.label }}</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="state-msg">Loading campaigns...</div>

      <!-- Empty -->
      <div v-else-if="campaigns.length === 0" class="state-msg">
        No campaigns yet. Create your first one above.
      </div>

      <!-- Campaign grid -->
      <div v-else class="campaign-grid">
        <div
          v-for="c in campaigns"
          :key="c.id"
          class="campaign-card"
          @click="$router.push(`/campaign/${c.id}`)"
        >
          <div class="card-top">
            <div class="card-status" :class="c.status">{{ c.status }}</div>
            <div class="card-impact" v-if="c.impact_score !== null">
              Impact: <span class="score">{{ c.impact_score }}</span>
            </div>
          </div>
          <div class="card-name">{{ c.name }}</div>
          <div class="card-brand">{{ c.brand }}</div>
          <div class="card-meta">
            <span v-if="c.channels?.length" class="tag-row">
              <span v-for="ch in c.channels.slice(0, 3)" :key="ch" class="tag">{{ ch }}</span>
            </span>
            <span v-if="c.markets?.length" class="tag-row">
              <span v-for="m in c.markets.slice(0, 2)" :key="m" class="tag market">{{ m }}</span>
            </span>
          </div>
          <div class="card-footer">
            <span>{{ c.asset_count }} assets · {{ c.mention_count }} mentions</span>
            <span class="card-dates" v-if="c.start_date">{{ c.start_date }} → {{ c.end_date || '…' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <span>New Campaign</span>
          <button class="modal-close" @click="showCreate = false">✕</button>
        </div>

        <div class="form-grid">
          <label class="form-label">Campaign Name *
            <input v-model="form.name" class="form-input" placeholder="e.g. Raya 2026 Promo" />
          </label>
          <label class="form-label">Brand *
            <input v-model="form.brand" class="form-input" placeholder="e.g. Bergaya Group" />
          </label>
          <label class="form-label">Objective
            <input v-model="form.objective" class="form-input" placeholder="e.g. Awareness + Conversion" />
          </label>
          <label class="form-label">Start Date
            <input v-model="form.start_date" type="date" class="form-input" />
          </label>
          <label class="form-label">End Date
            <input v-model="form.end_date" type="date" class="form-input" />
          </label>
          <label class="form-label">Channels (comma-separated)
            <input v-model="channelsRaw" class="form-input" placeholder="Meta, TikTok, Google" />
          </label>
          <label class="form-label">Markets (comma-separated)
            <input v-model="marketsRaw" class="form-input" placeholder="ID, MY, SG" />
          </label>
          <label class="form-label">Tags (comma-separated)
            <input v-model="tagsRaw" class="form-input" placeholder="ramadan, promo, food" />
          </label>
        </div>

        <div v-if="createError" class="form-error">{{ createError }}</div>

        <div class="modal-footer">
          <button class="btn-ghost" @click="showCreate = false">Cancel</button>
          <button class="btn-primary" :disabled="creating" @click="createCampaign">
            {{ creating ? 'Creating…' : 'Create Campaign' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { campaignApi } from '../api/campaign'

const router = useRouter()

const campaigns = ref([])
const loading = ref(false)
const statusFilter = ref('all')
const showCreate = ref(false)
const creating = ref(false)
const createError = ref('')

const form = ref({ name: '', brand: '', objective: '', start_date: '', end_date: '' })
const channelsRaw = ref('')
const marketsRaw = ref('')
const tagsRaw = ref('')

const statuses = [
  { value: 'all', label: 'All' },
  { value: 'draft', label: 'Draft' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' },
]

async function fetchCampaigns() {
  loading.value = true
  try {
    const params = statusFilter.value !== 'all' ? { status: statusFilter.value } : {}
    const res = await campaignApi.list(params)
    campaigns.value = res.data.data || []
  } catch {
    campaigns.value = []
  } finally {
    loading.value = false
  }
}

async function createCampaign() {
  createError.value = ''
  if (!form.value.name || !form.value.brand) {
    createError.value = 'Name and Brand are required.'
    return
  }
  creating.value = true
  try {
    const payload = {
      ...form.value,
      channels: channelsRaw.value.split(',').map(s => s.trim()).filter(Boolean),
      markets: marketsRaw.value.split(',').map(s => s.trim()).filter(Boolean),
      tags: tagsRaw.value.split(',').map(s => s.trim()).filter(Boolean),
    }
    const res = await campaignApi.create(payload)
    showCreate.value = false
    router.push(`/campaign/${res.data.data.id}`)
  } catch (err) {
    createError.value = err.response?.data?.error || 'Failed to create campaign.'
  } finally {
    creating.value = false
  }
}

watch(statusFilter, fetchCampaigns)
onMounted(fetchCampaigns)
</script>

<style scoped>
.campaigns-container { min-height: 100vh; background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }

.navbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 32px; border-bottom: 1px solid #222; }
.nav-brand { font-size: 14px; font-weight: 700; letter-spacing: 4px; }
.nav-links { display: flex; gap: 24px; }
.nav-link { color: #888; text-decoration: none; font-size: 12px; transition: color 0.2s; }
.nav-link:hover { color: #fff; }

.page-content { padding: 40px 32px; max-width: 1280px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
.orange-tag { background: #f60; color: #000; font-size: 10px; font-weight: 700; letter-spacing: 2px; padding: 3px 8px; }
.page-title { font-size: 36px; font-weight: 700; margin: 12px 0 8px; }
.page-desc { color: #666; font-size: 13px; }

.btn-primary { background: #f60; color: #000; border: none; padding: 10px 20px; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; letter-spacing: 1px; }
.btn-primary:hover { background: #e55a00; }
.btn-primary:disabled { opacity: 0.5; cursor: default; }
.btn-ghost { background: transparent; color: #fff; border: 1px solid #333; padding: 10px 20px; font-family: inherit; font-size: 12px; cursor: pointer; }
.btn-ghost:hover { border-color: #fff; }

.filter-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 28px; }
.filter-label { color: #555; font-size: 11px; letter-spacing: 1px; }
.filter-btn { background: transparent; color: #555; border: 1px solid #333; padding: 5px 12px; font-family: inherit; font-size: 11px; cursor: pointer; }
.filter-btn.active, .filter-btn:hover { color: #fff; border-color: #f60; }

.state-msg { color: #555; font-size: 13px; padding: 60px 0; text-align: center; }

.campaign-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }

.campaign-card { border: 1px solid #222; padding: 20px; cursor: pointer; transition: border-color 0.2s; }
.campaign-card:hover { border-color: #f60; }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-status { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; padding: 3px 8px; border: 1px solid #333; }
.card-status.active { border-color: #0f0; color: #0f0; }
.card-status.draft { border-color: #555; color: #555; }
.card-status.completed { border-color: #f60; color: #f60; }
.card-status.archived { border-color: #444; color: #444; }
.card-impact { font-size: 11px; color: #888; }
.score { color: #f60; font-weight: 700; }

.card-name { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.card-brand { font-size: 12px; color: #888; margin-bottom: 12px; }

.card-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.tag-row { display: flex; gap: 4px; flex-wrap: wrap; }
.tag { font-size: 10px; background: #111; border: 1px solid #333; padding: 2px 6px; color: #aaa; }
.tag.market { border-color: #f60; color: #f60; }

.card-footer { display: flex; justify-content: space-between; font-size: 11px; color: #555; border-top: 1px solid #1a1a1a; padding-top: 12px; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #0a0a0a; border: 1px solid #333; width: 560px; max-width: 95vw; max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #222; font-size: 14px; font-weight: 700; letter-spacing: 2px; }
.modal-close { background: none; border: none; color: #888; font-size: 18px; cursor: pointer; }
.modal-close:hover { color: #fff; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 24px; }
.form-label { display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #888; letter-spacing: 1px; grid-column: span 1; }
.form-label:first-child, .form-label:nth-child(7), .form-label:nth-child(8) { grid-column: span 2; }
.form-input { background: #111; border: 1px solid #333; color: #fff; padding: 8px 12px; font-family: inherit; font-size: 12px; }
.form-input:focus { outline: none; border-color: #f60; }

.form-error { margin: 0 24px; color: #f44; font-size: 12px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 20px 24px; border-top: 1px solid #222; }
</style>
