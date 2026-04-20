import { onMounted, onUnmounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useCampaignsStore } from '@/stores/campaigns'
import { useRouter } from 'vue-router'

export function useCommandPalette() {
  const ui = useUiStore()
  const router = useRouter()
  const campaigns = useCampaignsStore()

  function handler(e) {
    const isMac = navigator.platform?.toLowerCase().includes('mac')
    const mod = isMac ? e.metaKey : e.ctrlKey
    if (mod && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault()
      ui.commandPaletteOpen ? ui.closeCommandPalette() : ui.openCommandPalette()
    } else if (e.key === 'Escape' && ui.commandPaletteOpen) {
      ui.closeCommandPalette()
    }
  }

  onMounted(() => window.addEventListener('keydown', handler))
  onUnmounted(() => window.removeEventListener('keydown', handler))

  function sources() {
    const out = [
      { kind: 'nav', label: 'Campaigns', to: '/app/campaigns' },
      { kind: 'nav', label: 'Reality Seeds', to: '/app/reality-seeds' },
      { kind: 'nav', label: 'Graph browser', to: '/app/graph' },
      { kind: 'nav', label: 'Provider settings', to: '/app/settings/providers' },
      { kind: 'nav', label: 'Task routing', to: '/app/settings/routing' },
      { kind: 'nav', label: 'Demo mode', to: '/app/demo' },
    ]
    for (const c of campaigns.list || []) {
      out.push({ kind: 'campaign', label: c.name, sub: c.brand, to: `/app/campaigns/${c.id}/overview` })
    }
    return out
  }

  function execute(item) {
    ui.closeCommandPalette()
    if (item?.to) router.push(item.to)
  }

  return { sources, execute }
}
