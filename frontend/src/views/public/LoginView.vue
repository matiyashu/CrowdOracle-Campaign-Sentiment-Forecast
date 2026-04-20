<template>
  <div class="login">
    <div class="login__card">
      <span class="login__eyebrow">SIGN IN</span>
      <h1>Welcome back.</h1>
      <p class="login__beta">Beta — no password required.</p>

      <form @submit.prevent="onSubmit" class="login__form">
        <label>
          <span>Work email</span>
          <input v-model="email" type="email" required placeholder="you@brand.com" />
        </label>
        <label>
          <span>Password</span>
          <input v-model="password" type="password" placeholder="(any value, we're in beta)" />
        </label>

        <button type="submit" class="btn btn--primary" :disabled="submitting">
          {{ submitting ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <div class="login__foot">
        <span>New here?</span>
        <router-link to="/app/demo">Try a demo instead →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const submitting = ref(false)
const router = useRouter()
const auth = useAuthStore()

async function onSubmit() {
  submitting.value = true
  auth.login(email.value || 'demo@crowdoracle.ai')
  router.push('/app/campaigns')
}
</script>

<style scoped>
.login {
  min-height: calc(100vh - 64px);
  display: grid; place-items: center;
  padding: 40px 24px;
  background: radial-gradient(ellipse at top, rgba(255,106,0,0.08), transparent 70%);
  color: var(--co-text);
}
.login__card {
  width: 100%; max-width: 420px;
  padding: 40px;
  background: var(--co-surface);
  border: 1px solid var(--co-border);
}
.login__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.login__card h1 { font-size: 28px; margin: 12px 0 6px; letter-spacing: -0.02em; }
.login__beta { font-size: 12px; color: var(--co-accent); margin-bottom: 28px; }

.login__form { display: flex; flex-direction: column; gap: 16px; }
.login__form label { display: flex; flex-direction: column; gap: 6px; }
.login__form span { font-size: 12px; color: var(--co-text-dim); letter-spacing: 0.03em; }
.login__form input {
  padding: 10px 12px;
  background: var(--co-bg);
  border: 1px solid var(--co-border-2);
  color: var(--co-text);
  font-family: var(--co-font-mono); font-size: 13px;
}
.login__form input:focus { outline: none; border-color: var(--co-accent); }

.btn {
  margin-top: 8px;
  padding: 12px 18px;
  font-family: var(--co-font-mono); font-size: 13px;
  border-radius: var(--co-radius);
  cursor: pointer;
  border: 1px solid var(--co-accent);
  background: var(--co-accent); color: #000;
}
.btn:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); }
.btn:disabled { opacity: 0.6; cursor: wait; }

.login__foot {
  margin-top: 24px; text-align: center;
  font-size: 13px; color: var(--co-text-dim);
}
.login__foot a { color: var(--co-accent); margin-left: 6px; }
</style>
