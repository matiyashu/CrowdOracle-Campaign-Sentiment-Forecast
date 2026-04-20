import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const BASE = '/api/demo'

export const useDemoStore = defineStore('demo', () => {
  const active = ref(false)
  const packageId = ref(null)
  const packages = ref([])
  const loading = ref(false)

  async function loadPackages() {
    try {
      const { data } = await axios.get(`${BASE}/packages`)
      packages.value = data?.packages || []
    } catch (_) {
      packages.value = []
    }
  }

  async function load(pkgId) {
    loading.value = true
    try {
      const { data } = await axios.post(`${BASE}/load`, { package_id: pkgId })
      active.value = true
      packageId.value = pkgId
      try { localStorage.setItem('co.demo', JSON.stringify({ active: true, packageId: pkgId })) } catch (_) {}
      return data?.campaign_id || data?.campaignId
    } finally {
      loading.value = false
    }
  }

  async function reset() {
    try { await axios.post(`${BASE}/reset`) } catch (_) {}
    active.value = false
    packageId.value = null
    try { localStorage.removeItem('co.demo') } catch (_) {}
  }

  function hydrate() {
    try {
      const raw = localStorage.getItem('co.demo')
      if (raw) {
        const s = JSON.parse(raw)
        active.value = !!s.active
        packageId.value = s.packageId || null
      }
    } catch (_) {}
  }

  return { active, packageId, packages, loading, loadPackages, load, reset, hydrate }
})
