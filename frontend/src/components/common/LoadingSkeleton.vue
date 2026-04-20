<template>
  <div class="skel" :style="{ height, width }" />
</template>

<script setup>
defineProps({
  height: { type: String, default: '100%' },
  width: { type: String, default: '100%' },
})
</script>

<style scoped>
.skel {
  background: linear-gradient(90deg, var(--co-surface) 0%, var(--co-border) 50%, var(--co-surface) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
  border-radius: var(--co-radius);
  min-height: 14px;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
