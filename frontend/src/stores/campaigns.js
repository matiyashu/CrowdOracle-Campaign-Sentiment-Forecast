import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { campaignApi } from '@/api/campaign'

function unwrap(res) {
  return res?.data?.data ?? res?.data ?? null
}

export const useCampaignsStore = defineStore('campaigns', () => {
  const list = ref([])
  const current = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const byId = computed(() => (id) => list.value.find((c) => String(c.id) === String(id)))

  async function loadList(params) {
    loading.value = true
    error.value = null
    try {
      list.value = unwrap(await campaignApi.list(params)) || []
    } catch (e) {
      error.value = e
      list.value = []
    } finally {
      loading.value = false
    }
  }

  async function load(id) {
    loading.value = true
    error.value = null
    try {
      current.value = unwrap(await campaignApi.get(id))
      return current.value
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const created = unwrap(await campaignApi.create(payload))
    if (created) list.value = [created, ...list.value]
    return created
  }

  async function update(id, payload) {
    const updated = unwrap(await campaignApi.patch(id, payload))
    if (!updated) return null
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
