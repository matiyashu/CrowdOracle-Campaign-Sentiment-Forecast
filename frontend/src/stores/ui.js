import { defineStore } from 'pinia'
import { ref } from 'vue'

let _toastId = 0

export const useUiStore = defineStore('ui', () => {
  const sidebarCollapsed = ref(false)
  const commandPaletteOpen = ref(false)
  const toasts = ref([])

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function openCommandPalette() { commandPaletteOpen.value = true }
  function closeCommandPalette() { commandPaletteOpen.value = false }

  function addToast({ title, body, tone = 'info', ttl = 5000 }) {
    const id = ++_toastId
    toasts.value.push({ id, title, body, tone })
    if (ttl > 0) setTimeout(() => dismissToast(id), ttl)
    return id
  }

  function dismissToast(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return {
    sidebarCollapsed, commandPaletteOpen, toasts,
    toggleSidebar, openCommandPalette, closeCommandPalette,
    addToast, dismissToast,
  }
})
