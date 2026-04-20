import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ── Public marketing site ─────────────────────────────────────────────────
  {
    path: '/',
    component: () => import('@/layouts/PublicShell.vue'),
    children: [
      { path: '',        name: 'Landing',  component: () => import('@/views/public/LandingView.vue'),  meta: { shell: 'public' } },
      { path: 'product', name: 'Product',  component: () => import('@/views/public/ProductView.vue'),  meta: { shell: 'public' } },
      { path: 'pricing', name: 'Pricing',  component: () => import('@/views/public/PricingView.vue'),  meta: { shell: 'public' } },
      { path: 'docs',    name: 'Docs',     component: () => import('@/views/public/DocsView.vue'),     meta: { shell: 'public' } },
      { path: 'login',   name: 'Login',    component: () => import('@/views/public/LoginView.vue'),    meta: { shell: 'public' } },
    ],
  },

  // ── App shell (authenticated workspace) ───────────────────────────────────
  {
    path: '/app',
    component: () => import('@/layouts/AppShell.vue'),
    meta: { shell: 'app', requiresAuth: true },
    children: [
      { path: '',              redirect: '/app/campaigns' },
      { path: 'campaigns',     name: 'CampaignList',   component: () => import('@/views/app/CampaignListView.vue') },
      { path: 'campaigns/new', name: 'CampaignCreate', component: () => import('@/views/app/CampaignCreateView.vue') },
      {
        path: 'campaigns/:campaignId',
        component: () => import('@/views/app/CampaignWorkspace.vue'),
        props: true,
        children: [
          { path: '',          redirect: { name: 'CampaignOverview' } },
          { path: 'overview',  name: 'CampaignOverview',  component: () => import('@/views/app/campaign/OverviewTab.vue')  },
          { path: 'creatives', name: 'CampaignCreatives', component: () => import('@/views/app/campaign/CreativesTab.vue') },
          { path: 'mentions',  name: 'CampaignMentions',  component: () => import('@/views/app/campaign/MentionsTab.vue')  },
          { path: 'sentiment', name: 'CampaignSentiment', component: () => import('@/views/app/campaign/SentimentTab.vue') },
          { path: 'impact',    name: 'CampaignImpact',    component: () => import('@/views/app/campaign/ImpactTab.vue')    },
          { path: 'report',    name: 'CampaignReport',    component: () => import('@/views/app/campaign/ReportTab.vue')    },
        ],
      },
      {
        path: 'reality-seeds',
        component: () => import('@/views/app/realityseeds/RealitySeedsLayout.vue'),
        children: [
          { path: '',            redirect: { name: 'SeedsList' } },
          { path: 'seeds',       name: 'SeedsList',  component: () => import('@/views/app/realityseeds/SeedsListView.vue') },
          { path: 'seeds/new',   name: 'SeedCreate', component: () => import('@/views/app/realityseeds/SeedCreateView.vue') },
          {
            path: 'seeds/:id',
            name: 'SeedDetail',
            component: () => import('@/views/app/realityseeds/SeedDetailView.vue'),
            props: true,
            children: [
              { path: '',          redirect: (to) => ({ name: 'SeedGraph', params: { id: to.params.id } }) },
              { path: 'graph',     name: 'SeedGraph',     component: () => import('@/components/realityseeds/GraphPanel.vue') },
              { path: 'split',     name: 'SeedSplit',     component: () => import('@/components/realityseeds/SplitPanel.vue') },
              { path: 'workbench', name: 'SeedWorkbench', component: () => import('@/components/realityseeds/WorkbenchPanel.vue') },
            ],
          },
          { path: 'runs/:runId', name: 'SeedRun',    component: () => import('@/views/app/realityseeds/SeedRunView.vue'),    props: true },
        ],
      },
      { path: 'graph', name: 'GraphBrowser', component: () => import('@/views/app/GraphBrowserView.vue') },
      {
        path: 'settings',
        component: () => import('@/views/app/settings/SettingsLayout.vue'),
        children: [
          { path: '',          redirect: { name: 'SettingsProviders' } },
          { path: 'providers', name: 'SettingsProviders', component: () => import('@/views/app/settings/ProvidersView.vue') },
          { path: 'routing',   name: 'SettingsRouting',   component: () => import('@/views/app/settings/RoutingView.vue')   },
          { path: 'workspace', name: 'SettingsWorkspace', component: () => import('@/views/app/settings/WorkspaceView.vue') },
          { path: 'api-keys',  name: 'SettingsApiKeys',   component: () => import('@/views/app/settings/ApiKeysView.vue')   },
        ],
      },
      { path: 'demo', name: 'Demo', component: () => import('@/views/app/DemoView.vue') },
    ],
  },

  // ── Legacy redirects ──────────────────────────────────────────────────────
  { path: '/campaigns',                 redirect: '/app/campaigns' },
  { path: '/campaign/:campaignId',      redirect: (to) => `/app/campaigns/${to.params.campaignId}/overview` },
  { path: '/campaign/:campaignId/dashboard', redirect: (to) => `/app/campaigns/${to.params.campaignId}/overview` },
  { path: '/campaign/:campaignId/creatives', redirect: (to) => `/app/campaigns/${to.params.campaignId}/creatives` },
  { path: '/campaign/:campaignId/report',    redirect: (to) => `/app/campaigns/${to.params.campaignId}/report` },
  { path: '/settings/providers',        redirect: '/app/settings/providers' },
  { path: '/process/:projectId',        redirect: '/app/reality-seeds/seeds' },
  { path: '/simulation/:simulationId',  redirect: '/app/reality-seeds/seeds' },
  { path: '/simulation/:simulationId/start', redirect: '/app/reality-seeds/seeds' },
  { path: '/report/:reportId',          redirect: '/app/reality-seeds/seeds' },
  { path: '/interaction/:reportId',     redirect: '/app/reality-seeds/seeds' },

  // ── 404 ───────────────────────────────────────────────────────────────────
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/layouts/PublicShell.vue'),
    children: [
      { path: '', name: 'NotFound', component: () => import('@/views/public/NotFoundView.vue'), meta: { shell: 'public' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } },
})

// Stub auth guard — real auth to be wired in Sprint D
router.beforeEach((to, _from, next) => {
  // In beta, everyone is "authed" — we only gate future private routes.
  next()
})

export default router
