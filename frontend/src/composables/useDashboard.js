import { computed, watch } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

export function useDashboard(campaignIdRef) {
  const analytics = useAnalyticsStore()

  const data = computed(() => analytics.dashboardByCampaign[campaignIdRef.value])
  const loading = computed(() => analytics.loading)
  const error = computed(() => analytics.error)

  async function refresh() {
    if (!campaignIdRef.value) return
    await analytics.loadDashboard(campaignIdRef.value)
  }

  watch(campaignIdRef, (id) => { if (id) refresh() }, { immediate: true })

  return { data, loading, error, refresh }
}
