import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'

// BigBrother marketing intelligence views
import CampaignListView from '../views/CampaignListView.vue'
import CampaignDetailView from '../views/CampaignDetailView.vue'
import CreativeLibraryView from '../views/CreativeLibraryView.vue'
import DashboardView from '../views/DashboardView.vue'
import ReportBuilderView from '../views/ReportBuilderView.vue'
import ProviderSettingsView from '../views/ProviderSettingsView.vue'

const routes = [
  // ── Core simulation routes (Home, Process, Simulation, Report) ───────────
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

  // ── BigBrother marketing intelligence routes ──────────────────────────────
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
    path: '/campaign/:campaignId/creatives',
    name: 'CreativeLibrary',
    component: CreativeLibraryView,
    props: true
  },
  {
    path: '/campaign/:campaignId/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    props: true
  },
  {
    path: '/campaign/:campaignId/report',
    name: 'ReportBuilder',
    component: ReportBuilderView,
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
