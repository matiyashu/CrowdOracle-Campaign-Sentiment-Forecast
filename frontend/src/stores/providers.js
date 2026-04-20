import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { providersApi } from '@/api/providers'

// The service wrapper already unwraps { success, data } → just read .data
const unwrap = (res) => res?.data ?? res ?? null

export const useProvidersStore = defineStore('providers', () => {
  const list = ref([])
  const taskRouting = ref({})
  const loading = ref(false)
  const error = ref(null)
  const lastTest = ref(null)

  const active = computed(() => list.value.find((p) => p.is_active) || null)

  async function loadList() {
    loading.value = true
    error.value = null
    try {
      const res = await providersApi.list()
      const data = unwrap(res)
      list.value = Array.isArray(data) ? data : (data?.providers || [])
      taskRouting.value = active.value?.task_routing || {}
    } catch (e) {
      error.value = e
      list.value = []
    } finally {
      loading.value = false
    }
  }

  async function save(payload) {
    const res = await providersApi.save(payload)
    await loadList()
    return unwrap(res)
  }

  async function patch(id, payload) {
    const res = await providersApi.patch(id, payload)
    await loadList()
    return unwrap(res)
  }

  async function test(payload) {
    const res = await providersApi.testConnection(payload)
    const data = unwrap(res)
    lastTest.value = {
      ok: !!data?.ok,
      detail: data?.detail || data?.message || (data?.ok ? 'Connected.' : 'Connection failed.'),
      latency_ms: data?.latency_ms,
      at: Date.now(),
    }
    return data
  }

  async function setActive(providerId) {
    await providersApi.setActive(providerId)
    await loadList()
  }

  async function remove(id) {
    await providersApi.remove(id)
    list.value = list.value.filter((p) => String(p.id) !== String(id))
  }

  async function saveRouting(routing) {
    await providersApi.saveTaskRouting(routing)
    taskRouting.value = { ...routing }
    await loadList()
  }

  return {
    list, active, taskRouting, loading, error, lastTest,
    loadList, save, patch, test, setActive, remove, saveRouting,
  }
})
