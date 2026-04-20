import { defineStore } from 'pinia'
import { ref } from 'vue'
import service from '../api'

const BASE = '/api/demo'
const LS_KEY = 'crowdoracle.demo'

const unwrap = (res) => res?.data ?? null

export const useDemoStore = defineStore('demo', () => {
  const active = ref(false)
  const packageId = ref(null)
  const campaignId = ref(null)
  const packages = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function loadPackages() {
    error.value = null
    try {
      const res = await service.get(`${BASE}/packages`)
      const data = unwrap(res)
      packages.value = Array.isArray(data) ? data : (data?.packages || [])
    } catch (e) {
      error.value = e?.message || 'Failed to load demo packages.'
      packages.value = []
    }
  }

  async function load(pkgId) {
    loading.value = true
    error.value = null
    try {
      const res = await service.post(`${BASE}/load`, { package_id: pkgId })
      const data = unwrap(res)
      const cid = data?.campaign_id ?? data?.campaignId ?? null
      active.value = true
      packageId.value = pkgId
      campaignId.value = cid
      try {
        localStorage.setItem(LS_KEY, JSON.stringify({ active: true, packageId: pkgId, campaignId: cid }))
      } catch (_) {}
      return cid
    } catch (e) {
      error.value = e?.message || 'Could not load this demo package.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function reset(targetCampaignId = null) {
    error.value = null
    try {
      const body = targetCampaignId ? { campaign_id: targetCampaignId } : {}
      await service.post(`${BASE}/reset`, body)
    } catch (e) {
      error.value = e?.message || 'Could not reset demo data.'
    }
    active.value = false
    packageId.value = null
    campaignId.value = null
    try { localStorage.removeItem(LS_KEY) } catch (_) {}
  }

  function hydrate() {
    try {
      const raw = localStorage.getItem(LS_KEY)
      if (!raw) return
      const s = JSON.parse(raw)
      active.value = !!s.active
      packageId.value = s.packageId || null
      campaignId.value = s.campaignId || null
    } catch (_) {}
  }

  return {
    active, packageId, campaignId, packages, loading, error,
    loadPackages, load, reset, hydrate,
  }
})
