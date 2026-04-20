import { defineStore } from 'pinia'
import { ref } from 'vue'
import { creativesApi } from '@/api/creatives'

function unwrap(res) {
  return res?.data?.data ?? res?.data ?? null
}

export const useCreativesStore = defineStore('creatives', () => {
  const byCampaign = ref({})
  const loading = ref(false)
  const error = ref(null)

  async function loadByCampaign(campaignId) {
    loading.value = true
    error.value = null
    try {
      byCampaign.value[campaignId] = unwrap(await creativesApi.byCampaign(campaignId)) || []
    } catch (e) {
      error.value = e
      byCampaign.value[campaignId] = []
    } finally {
      loading.value = false
    }
  }

  async function upload(campaignId, file) {
    const fd = new FormData()
    fd.append('campaign_id', String(campaignId))
    fd.append('file', file)
    return unwrap(await creativesApi.upload(fd))
  }

  async function analyze(assetId) {
    return unwrap(await creativesApi.analyze(assetId))
  }

  async function batchAnalyze(assetIds) {
    return unwrap(await creativesApi.batchAnalyze(assetIds))
  }

  async function updateTags(assetId, tags) {
    return unwrap(await creativesApi.updateTags(assetId, tags))
  }

  return { byCampaign, loading, error, loadByCampaign, upload, analyze, batchAnalyze, updateTags }
})
