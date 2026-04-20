import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsApi } from '@/api/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  const dashboardByCampaign = ref({})
  const loading = ref(false)
  const error = ref(null)

  async function loadDashboard(campaignId) {
    loading.value = true
    error.value = null
    try {
      const { data } = await analyticsApi.dashboard(campaignId)
      dashboardByCampaign.value[campaignId] = data?.dashboard || data
      return dashboardByCampaign.value[campaignId]
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loading.value = false
    }
  }

  async function exportMarkdown(campaignId) {
    const { data } = await analyticsApi.exportDashboardMarkdown(campaignId)
    return data
  }

  async function generateReport(payload) {
    const { data } = await analyticsApi.generateReport(payload)
    return data
  }

  return { dashboardByCampaign, loading, error, loadDashboard, exportMarkdown, generateReport }
})
