import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { campaignApi } from '@/api/campaign'

export const useCampaignsStore = defineStore('campaigns', () => {
  const list = ref([])
  const current = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const byId = computed(() => (id) => list.value.find((c) => String(c.id) === String(id)))

  async function loadList() {
    loading.value = true
    error.value = null
    try {
      const { data } = await campaignApi.list()
      list.value = data?.campaigns || data || []
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  async function load(id) {
    loading.value = true
    error.value = null
    try {
      const { data } = await campaignApi.get(id)
      current.value = data?.campaign || data
      return current.value
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const { data } = await campaignApi.create(payload)
    const created = data?.campaign || data
    list.value = [created, ...list.value]
    return created
  }

  async function update(id, payload) {
    const { data } = await campaignApi.patch(id, payload)
    const updated = data?.campaign || data
    const i = list.value.findIndex((c) => String(c.id) === String(id))
    if (i !== -1) list.value[i] = updated
    if (current.value && String(current.value.id) === String(id)) current.value = updated
    return updated
  }

  async function remove(id) {
    await campaignApi.remove(id)
    list.value = list.value.filter((c) => String(c.id) !== String(id))
    if (current.value && String(current.value.id) === String(id)) current.value = null
  }

  return { list, current, loading, error, byId, loadList, load, create, update, remove }
})
