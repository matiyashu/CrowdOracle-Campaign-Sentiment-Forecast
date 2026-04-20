<template>
  <router-view />
</template>

<script setup>
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

html, body, #app {
  min-height: 100vh;
  background: var(--co-bg);
  color: var(--co-text);
}

#app {
  font-family: var(--co-font-mono);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

button { font-family: inherit; }
</style>
