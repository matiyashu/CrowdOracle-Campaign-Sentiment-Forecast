<template>
  <div class="shell">
    <Sidebar />
    <div class="shell__main">
      <TopBar />
      <main class="shell__body">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </main>
    </div>
    <CommandPalette />
    <ToastStack />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Sidebar from '@/components/shell/Sidebar.vue'
import TopBar from '@/components/shell/TopBar.vue'
import CommandPalette from '@/components/shell/CommandPalette.vue'
import ToastStack from '@/components/common/ToastStack.vue'
import { useApi } from '@/composables/useApi'
import { useCommandPalette } from '@/composables/useCommandPalette'
import { useAuthStore } from '@/stores/auth'
import { useDemoStore } from '@/stores/demo'
import { useLocale } from '@/composables/useLocale'

useApi()
useCommandPalette()

const auth = useAuthStore()
const demo = useDemoStore()
const locale = useLocale()

onMounted(() => {
  auth.hydrate()
  demo.hydrate()
  locale.hydrate()
})
</script>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
  background: var(--co-bg);
}
.shell__main {
  flex: 1;
  display: flex; flex-direction: column;
  min-width: 0;
}
.shell__body {
  flex: 1;
  padding: 24px 32px;
  overflow-x: hidden;
}

@media (max-width: 900px) {
  .shell__body { padding: 16px; }
}
</style>
