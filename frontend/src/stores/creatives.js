import { defineStore } from 'pinia'
import { ref } from 'vue'
import { creativesApi } from '@/api/creatives'

export const useCreativesStore = defineStore('creatives', () => {
  const byCampaign = ref({})
  const analysisTasks = ref({})
  const loading = ref(false)

  async function loadByCampaign(campaignId) {
    loading.value = true
    try {
      const { data } = await creativesApi.byCampaign(campaignId)
      byCampaign.value[campaignId] = data?.creatives || data || []
    } finally {
      loading.value = false
    }
  }

  async function upload(formData) {
    const { data } = await creativesApi.upload(formData)
    return data
  }

  async function analyze(assetId) {
    const { data } = await creativesApi.analyze(assetId)
    analysisTasks.value[assetId] = data?.task_id || null
    return data
  }

  async function updateTags(assetId, tags) {
    const { data } = await creativesApi.updateTags(assetId, tags)
    return data
  }

  return { byCampaign, analysisTasks, loading, loadByCampaign, upload, analyze, updateTags }
})
