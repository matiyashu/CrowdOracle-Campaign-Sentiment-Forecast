import { useUiStore } from '@/stores/ui'

export function useToasts() {
  const ui = useUiStore()
  return {
    toasts: ui.toasts,
    add: ui.addToast,
    dismiss: ui.dismissToast,
    success: (title, body) => ui.addToast({ title, body, tone: 'success' }),
    error:   (title, body) => ui.addToast({ title, body, tone: 'error' }),
    info:    (title, body) => ui.addToast({ title, body, tone: 'info' }),
  }
}
