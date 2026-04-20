<template>
  <nav class="crumbs" aria-label="Breadcrumb">
    <template v-for="(c, i) in crumbs" :key="`${c.to}-${i}`">
      <router-link v-if="i < crumbs.length - 1" :to="c.to" class="crumbs__item">{{ c.label }}</router-link>
      <span v-else class="crumbs__item crumbs__item--current">{{ c.label }}</span>
      <span v-if="i < crumbs.length - 1" class="crumbs__sep">/</span>
    </template>
  </nav>
</template>

<script setup>
import { useBreadcrumbs } from '@/composables/useBreadcrumbs'
const { crumbs } = useBreadcrumbs()
</script>

<style scoped>
.crumbs {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px;
  color: var(--co-text-dim);
}
.crumbs__item { color: var(--co-text-dim); }
.crumbs__item:hover { color: var(--co-accent); }
.crumbs__item--current { color: var(--co-text); }
.crumbs__sep { color: var(--co-text-mute); }
</style>
