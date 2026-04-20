import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useRealitySeedsStore = defineStore('realitySeeds', () => {
  const seeds = ref([])
  const runs = ref([])
  const loading = ref(false)

  const byId = computed(() => (id) => seeds.value.find((s) => String(s.id) === String(id)))

  async function loadSeeds() {
    loading.value = true
    try {
      const { data } = await axios.get('/api/graph/projects')
      seeds.value = data?.projects || []
    } catch (_) {
      seeds.value = []
    } finally {
      loading.value = false
    }
  }

  async function uploadSeed(formData) {
    const { data } = await axios.post('/api/graph/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  }

  async function startRun(seedId, config) {
    const { data } = await axios.post('/api/simulation/start', { project_id: seedId, ...config })
    return data
  }

  return { seeds, runs, loading, byId, loadSeeds, uploadSeed, startRun }
})
