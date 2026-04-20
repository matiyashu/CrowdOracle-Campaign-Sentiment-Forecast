import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { providersApi } from '@/api/providers'

export const useProvidersStore = defineStore('providers', () => {
  const list = ref([])
  const taskRouting = ref({})
  const loading = ref(false)
  const lastTest = ref(null)

  const active = computed(() => list.value.find((p) => p.is_active) || null)

  async function loadList() {
    loading.value = true
    try {
      const { data } = await providersApi.list()
      list.value = data?.providers || data || []
      taskRouting.value = data?.task_routing || {}
    } finally {
      loading.value = false
    }
  }

  async function save(payload) {
    const { data } = await providersApi.save(payload)
    await loadList()
    return data
  }

  async function test(payload) {
    const { data } = await providersApi.testConnection(payload)
    lastTest.value = { ok: !!data?.ok, detail: data?.detail || data?.message, at: Date.now() }
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
    taskRouting.value = routing
  }

  return { list, active, taskRouting, loading, lastTest, loadList, save, test, setActive, remove, saveRouting }
})
