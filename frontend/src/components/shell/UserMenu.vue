<template>
  <div class="user" @click.outside="open = false">
    <button class="user__btn" @click="open = !open" aria-haspopup="true">
      <span class="user__avatar">{{ initial }}</span>
      <span v-if="auth.user" class="user__name">{{ auth.user.name }}</span>
    </button>
    <div v-if="open" class="user__menu">
      <router-link to="/app/settings" class="user__item" @click="open = false">Settings</router-link>
      <router-link to="/app/settings/workspace" class="user__item" @click="open = false">Workspace</router-link>
      <button class="user__item user__item--danger" @click="signOut">Sign out</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const open = ref(false)

const initial = computed(() => {
  const n = auth.user?.name || auth.user?.email || '?'
  return n.charAt(0).toUpperCase()
})

function signOut() {
  auth.logout()
  open.value = false
  router.push('/')
}
</script>

<style scoped>
.user { position: relative; }
.user__btn {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 8px;
  background: transparent; border: 1px solid var(--co-border-2);
  color: var(--co-text); cursor: pointer;
  border-radius: var(--co-radius);
  font-family: var(--co-font-mono);
  font-size: 12px;
}
.user__btn:hover { border-color: var(--co-accent); }
.user__avatar {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--co-accent); color: #000;
  display: grid; place-items: center;
  font-weight: 700; font-size: 11px;
}
.user__name { max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.user__menu {
  position: absolute; top: calc(100% + 6px); right: 0;
  min-width: 180px;
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  box-shadow: var(--co-shadow);
  display: flex; flex-direction: column;
  z-index: 60;
}
.user__item {
  padding: 10px 14px;
  font-size: 13px;
  color: var(--co-text);
  background: none; border: none; text-align: left;
  cursor: pointer; font-family: var(--co-font-mono);
}
.user__item:hover { background: rgba(255,106,0,0.06); color: var(--co-accent); }
.user__item--danger { border-top: 1px solid var(--co-border); color: var(--co-error); }
.user__item--danger:hover { color: var(--co-error); background: rgba(255,77,79,0.06); }
</style>
