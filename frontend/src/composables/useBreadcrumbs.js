import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCampaignsStore } from '@/stores/campaigns'

const LABELS = {
  CampaignList: 'Campaigns',
  CampaignCreate: 'New campaign',
  CampaignOverview: 'Overview',
  CampaignCreatives: 'Creatives',
  CampaignMentions: 'Mentions',
  CampaignSentiment: 'Sentiment',
  CampaignImpact: 'Impact',
  CampaignReport: 'Report',
  SeedsList: 'Reality Seeds',
  SeedCreate: 'New seed',
  SeedDetail: 'Seed',
  SeedRun: 'Run',
  GraphBrowser: 'Graph',
  SettingsProviders: 'Providers',
  SettingsRouting: 'Routing',
  SettingsWorkspace: 'Workspace',
  SettingsApiKeys: 'API keys',
  Demo: 'Demo mode',
}

export function useBreadcrumbs() {
  const route = useRoute()
  const campaigns = useCampaignsStore()

  const crumbs = computed(() => {
    const out = []
    const matched = route.matched.filter((r) => r.name && r.name !== '')
    if (route.path.startsWith('/app')) out.push({ label: 'App', to: '/app' })

    for (const m of matched) {
      let label = LABELS[m.name] || m.name
      let to = m.path
      if (m.name === 'CampaignOverview' || m.name?.startsWith('Campaign')) {
        const cid = route.params.campaignId
        if (cid && campaigns.current?.id && String(campaigns.current.id) === String(cid)) {
          if (!out.some((c) => c.label === campaigns.current.name)) {
            out.push({ label: campaigns.current.name, to: `/app/campaigns/${cid}/overview` })
          }
        }
      }
      to = to
        .replace(':campaignId', route.params.campaignId || '')
        .replace(':id', route.params.id || '')
        .replace(':runId', route.params.runId || '')
      out.push({ label, to })
    }
    const seen = new Set()
    return out.filter((c) => {
      const k = `${c.label}|${c.to}`
      if (seen.has(k)) return false
      seen.add(k)
      return true
    })
  })

  return { crumbs }
}
