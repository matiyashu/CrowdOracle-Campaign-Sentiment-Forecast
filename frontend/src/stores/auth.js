import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isDemo = ref(false)
  const isAuthenticated = computed(() => user.value !== null)

  function login(email) {
    user.value = { email, name: email.split('@')[0] }
    isDemo.value = false
    try { localStorage.setItem('co.auth', JSON.stringify(user.value)) } catch (_) {}
  }

  function logout() {
    user.value = null
    isDemo.value = false
    try { localStorage.removeItem('co.auth') } catch (_) {}
  }

  function hydrate() {
    try {
      const raw = localStorage.getItem('co.auth')
      if (raw) user.value = JSON.parse(raw)
    } catch (_) {}
  }

  return { user, isDemo, isAuthenticated, login, logout, hydrate }
})
