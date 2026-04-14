import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'

// CrowdOracle marketing intelligence views
import CampaignListView from '../views/CampaignListView.vue'
import CampaignDetailView from '../views/CampaignDetailView.vue'
import ProviderSettingsView from '../views/ProviderSettingsView.vue'

const routes = [
  // ── MiroFish core routes (unchanged) ──────────────────────────────────────
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  },

  // ── CrowdOracle marketing intelligence routes ──────────────────────────────
  {
    path: '/campaigns',
    name: 'CampaignList',
    component: CampaignListView
  },
  {
    path: '/campaign/:campaignId',
    name: 'CampaignDetail',
    component: CampaignDetailView,
    props: true
  },
  {
    path: '/settings/providers',
    name: 'ProviderSettings',
    component: ProviderSettingsView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
