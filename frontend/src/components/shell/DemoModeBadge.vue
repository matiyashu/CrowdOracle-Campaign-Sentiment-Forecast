<template>
  <button class="dmb" @click="exit" title="Exit demo mode">
    <span class="dmb__dot" />
    <span class="dmb__label">Demo</span>
  </button>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useDemoStore } from '@/stores/demo'

const router = useRouter()
const demo = useDemoStore()

async function exit() {
  await demo.reset()
  router.push('/app/campaigns')
}
</script>

<style scoped>
.dmb {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 10px;
  background: transparent;
  border: 1px solid var(--co-accent);
  color: var(--co-accent);
  font-family: var(--co-font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-radius: 999px;
  cursor: pointer;
}
.dmb:hover { background: var(--co-accent); color: #000; }
.dmb__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
</style>
