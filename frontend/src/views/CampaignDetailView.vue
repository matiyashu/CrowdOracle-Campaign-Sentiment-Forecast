<template>
  <div class="detail-container">
    <nav class="navbar">
      <div class="nav-brand">CROWDORACLE</div>
      <div class="nav-links">
        <router-link to="/campaigns" class="nav-link">← All Campaigns</router-link>
        <router-link :to="`/campaign/${campaignId}/dashboard`" class="nav-link">Dashboard</router-link>
        <router-link :to="`/campaign/${campaignId}/creatives`" class="nav-link">Creatives</router-link>
      </div>
    </nav>

    <div v-if="loading" class="state-msg">Loading campaign...</div>

    <div v-else-if="!campaign" class="state-msg">Campaign not found.</div>

    <div v-else class="page-content">
      <!-- Header -->
      <div class="camp-header">
        <div>
          <div class="header-top">
            <span class="camp-status" :class="campaign.status">{{ campaign.status }}</span>
            <span v-for="m in campaign.markets || []" :key="m" class="tag market">{{ m }}</span>
          </div>
          <h1 class="camp-name">{{ campaign.name }}</h1>
          <p class="camp-brand">{{ campaign.brand }}</p>
          <p v-if="campaign.objective" class="camp-objective">{{ campaign.objective }}</p>
        </div>
        <div class="header-actions">
          <router-link :to="`/campaign/${campaignId}/dashboard`" class="btn-primary">View Dashboard →</router-link>
        </div>
      </div>

      <!-- Stats row -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-val">{{ campaign.asset_count }}</div>
          <div class="stat-label">Creatives</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">{{ campaign.mention_count }}</div>
          <div class="stat-label">Mentions</div>
        </div>
        <div class="stat-card">
          <div class="stat-val">{{ campaign.channels?.length || 0 }}</div>
          <div class="stat-label">Channels</div>
        </div>
        <div class="stat-card" v-if="campaign.start_date">
          <div class="stat-val">{{ campaign.start_date }}</div>
          <div class="stat-label">Start Date</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tab-bar">
        <button v-for="tab in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === tab }" @click="activeTab = tab">{{ tab }}</button>
      </div>

      <!-- Tab: Creatives -->
      <div v-if="activeTab === 'Creatives'" class="tab-content">
        <div class="section-actions">
          <label class="btn-primary upload-label">
            + Upload Creative
            <input type="file" style="display:none" accept="image/*,video/*,.txt,.md" @change="uploadCreative" />
          </label>
          <router-link :to="`/campaign/${campaignId}/creatives`" class="btn-ghost">View Library →</router-link>
        </div>
        <p class="section-hint">Supported: images, videos, copy text, landing page docs.</p>
      </div>

      <!-- Tab: Mentions -->
      <div v-if="activeTab === 'Mentions'" class="tab-content">
        <div class="section-actions">
          <label class="btn-primary upload-label">
            + Import Mentions CSV
            <input type="file" accept=".csv,.xlsx" style="display:none" @change="uploadMentions" />
          </label>
        </div>
        <p class="section-hint">Required column: <code>text</code>. Optional: source_platform, author_handle, engagement_count, url.</p>
        <p v-if="uploadMsg" class="upload-msg">{{ uploadMsg }}</p>
      </div>

      <!-- Tab: Performance -->
      <div v-if="activeTab === 'Performance'" class="tab-content">
        <div class="section-actions">
          <label class="btn-primary upload-label">
            + Import Performance CSV
            <input type="file" accept=".csv,.xlsx" style="display:none" @change="uploadPerformance" />
          </label>
        </div>
        <p class="section-hint">Required columns: <code>date</code>, <code>channel</code>. Optional: spend, impressions, clicks, ctr, cpc, conversions, cpa, roas, revenue.</p>
        <p v-if="uploadMsg" class="upload-msg">{{ uploadMsg }}</p>
      </div>

      <!-- Tab: Settings -->
      <div v-if="activeTab === 'Settings'" class="tab-content">
        <div class="settings-form">
          <label class="form-label">Campaign Name
            <input v-model="editForm.name" class="form-input" />
          </label>
          <label class="form-label">Objective
            <input v-model="editForm.objective" class="form-input" />
          </label>
          <label class="form-label">Status
            <select v-model="editForm.status" class="form-input">
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
          </label>
          <button class="btn-primary" @click="saveCampaign">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { campaignApi } from '../api/campaign'
import { creativesApi } from '../api/creatives'
import { analyticsApi } from '../api/analytics'

const props = defineProps({ campaignId: { type: String, required: true } })

const campaign = ref(null)
const loading = ref(true)
const activeTab = ref('Creatives')
const uploadMsg = ref('')
const tabs = ['Creatives', 'Mentions', 'Performance', 'Settings']
const editForm = ref({})

async function loadCampaign() {
  loading.value = true
  try {
    const res = await campaignApi.get(props.campaignId)
    campaign.value = res.data.data
    editForm.value = { name: campaign.value.name, objective: campaign.value.objective, status: campaign.value.status }
  } catch {
    campaign.value = null
  } finally {
    loading.value = false
  }
}

async function uploadCreative(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const form = new FormData()
  form.append('campaign_id', props.campaignId)
  form.append('file', file)
  try {
    await creativesApi.upload(form)
    uploadMsg.value = `✓ ${file.name} uploaded.`
    await loadCampaign()
  } catch (err) {
    uploadMsg.value = `✗ Upload failed: ${err.response?.data?.error || err.message}`
  }
}

async function uploadMentions(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadMsg.value = 'Importing…'
  try {
    const res = await analyticsApi.uploadMentions(props.campaignId, file)
    uploadMsg.value = `✓ Imported ${res.data.data.inserted} mentions.`
    await loadCampaign()
  } catch (err) {
    uploadMsg.value = `✗ ${err.response?.data?.error || err.message}`
  }
}

async function uploadPerformance(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadMsg.value = 'Importing…'
  try {
    const res = await analyticsApi.uploadPerformance(props.campaignId, file)
    uploadMsg.value = `✓ Imported ${res.data.data.inserted} rows.`
  } catch (err) {
    uploadMsg.value = `✗ ${err.response?.data?.error || err.message}`
  }
}

async function saveCampaign() {
  try {
    const res = await campaignApi.patch(props.campaignId, editForm.value)
    campaign.value = res.data.data
    uploadMsg.value = '✓ Saved.'
  } catch (err) {
    uploadMsg.value = `✗ ${err.response?.data?.error || err.message}`
  }
}

onMounted(loadCampaign)
</script>

<style scoped>
.detail-container { min-height: 100vh; background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 32px; border-bottom: 1px solid #222; }
.nav-brand { font-size: 14px; font-weight: 700; letter-spacing: 4px; }
.nav-links { display: flex; gap: 24px; }
.nav-link { color: #888; text-decoration: none; font-size: 12px; }
.nav-link:hover { color: #fff; }
.state-msg { color: #555; text-align: center; padding: 80px; }
.page-content { padding: 40px 32px; max-width: 1280px; margin: 0 auto; }

.camp-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
.header-top { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.camp-status { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; padding: 3px 8px; border: 1px solid #333; }
.camp-status.active { border-color: #0f0; color: #0f0; }
.camp-status.draft { border-color: #555; color: #555; }
.tag.market { font-size: 10px; background: #111; border: 1px solid #f60; color: #f60; padding: 2px 6px; }
.camp-name { font-size: 32px; font-weight: 700; margin: 0 0 4px; }
.camp-brand { color: #888; font-size: 14px; margin: 0 0 4px; }
.camp-objective { color: #555; font-size: 12px; margin: 0; }

.stats-row { display: flex; gap: 16px; margin-bottom: 32px; }
.stat-card { flex: 1; border: 1px solid #222; padding: 20px; text-align: center; }
.stat-val { font-size: 28px; font-weight: 700; color: #f60; }
.stat-label { font-size: 11px; color: #555; margin-top: 4px; letter-spacing: 1px; }

.tab-bar { display: flex; border-bottom: 1px solid #222; margin-bottom: 28px; }
.tab-btn { background: none; border: none; color: #555; padding: 12px 20px; font-family: inherit; font-size: 12px; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }
.tab-btn.active { color: #fff; border-bottom-color: #f60; }
.tab-btn:hover { color: #fff; }

.tab-content { padding: 8px 0; }
.section-actions { display: flex; gap: 12px; margin-bottom: 16px; }
.section-hint { color: #555; font-size: 12px; }
.section-hint code { color: #f60; }

.upload-label { cursor: pointer; display: inline-block; }
.upload-msg { margin-top: 12px; font-size: 12px; color: #0f0; }

.settings-form { display: flex; flex-direction: column; gap: 16px; max-width: 480px; }
.form-label { display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #888; letter-spacing: 1px; }
.form-input { background: #111; border: 1px solid #333; color: #fff; padding: 8px 12px; font-family: inherit; font-size: 12px; }
.form-input:focus { outline: none; border-color: #f60; }

.btn-primary { background: #f60; color: #000; border: none; padding: 10px 20px; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-block; }
.btn-primary:hover { background: #e55a00; }
.btn-ghost { background: transparent; color: #fff; border: 1px solid #333; padding: 10px 20px; font-family: inherit; font-size: 12px; cursor: pointer; text-decoration: none; display: inline-block; }
.btn-ghost:hover { border-color: #fff; }
</style>
