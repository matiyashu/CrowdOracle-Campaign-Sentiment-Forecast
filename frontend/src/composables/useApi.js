import axios from 'axios'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'

let installed = false

export function useApi() {
  if (!installed) {
    const ui = useUiStore()
    const auth = useAuthStore()

    axios.interceptors.response.use(
      (r) => r,
      (err) => {
        const status = err?.response?.status
        if (status === 401) {
          auth.logout()
          if (typeof window !== 'undefined' && window.location.pathname.startsWith('/app')) {
            window.location.href = '/login'
          }
        } else if (status >= 500) {
          ui.addToast({
            title: 'Server error',
            body: err?.response?.data?.message || `Request failed (${status})`,
            tone: 'error',
          })
        }
        return Promise.reject(err)
      }
    )
    installed = true
  }
  return axios
}
