<template>
  <section class="section">
    <h4 v-if="!collapsed && label" class="section__label">{{ label }}</h4>
    <div class="section__items"><slot /></div>
  </section>
</template>

<script setup>
defineProps({ label: String, collapsed: Boolean })
</script>

<style scoped>
.section { padding: 8px 0; }
.section__label {
  padding: 0 16px 6px;
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--co-text-mute);
  font-weight: 500;
}
.section__items { display: flex; flex-direction: column; }
</style>
