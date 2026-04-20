<template>
  <section class="page">
    <header class="page__head">
      <span class="page__eyebrow">WORKSPACE / NEW</span>
      <h1>Create a campaign</h1>
      <p>Three steps. You can edit any of this later.</p>
    </header>

    <div class="steps">
      <button
        v-for="(s, i) in steps"
        :key="s"
        class="step"
        :class="{ 'step--on': step === i, 'step--done': step > i }"
        @click="step = i"
      ><span>{{ i + 1 }}</span> {{ s }}</button>
    </div>

    <form class="form" @submit.prevent="next">
      <!-- Step 0: basics -->
      <div v-if="step === 0" class="form__grid">
        <label class="field field--wide">
          <span>Campaign name *</span>
          <input v-model="form.name" required placeholder="e.g. Coastline Summer 26" />
        </label>
        <label class="field">
          <span>Brand *</span>
          <input v-model="form.brand" required placeholder="e.g. Coastline" />
        </label>
        <label class="field">
          <span>Objective</span>
          <input v-model="form.objective" placeholder="awareness, conversion, recall…" />
        </label>
      </div>

      <!-- Step 1: channels + dates -->
      <div v-else-if="step === 1" class="form__grid">
        <label class="field">
          <span>Start date</span>
          <input v-model="form.start_date" type="date" />
        </label>
        <label class="field">
          <span>End date</span>
          <input v-model="form.end_date" type="date" />
        </label>
        <label class="field field--wide">
          <span>Channels (comma-separated)</span>
          <input v-model="raw.channels" placeholder="instagram, tiktok, youtube" />
        </label>
        <label class="field field--wide">
          <span>Markets (comma-separated)</span>
          <input v-model="raw.markets" placeholder="US, UK, AU" />
        </label>
      </div>

      <!-- Step 2: tags -->
      <div v-else class="form__grid">
        <label class="field field--wide">
          <span>Tags (comma-separated)</span>
          <input v-model="raw.tags" placeholder="launch, summer, lifestyle" />
        </label>
        <div class="summary field--wide">
          <h3>Ready to create</h3>
          <dl>
            <dt>Name</dt><dd>{{ form.name || '—' }}</dd>
            <dt>Brand</dt><dd>{{ form.brand || '—' }}</dd>
            <dt>Objective</dt><dd>{{ form.objective || '—' }}</dd>
            <dt>Window</dt><dd>{{ form.start_date || '?' }} → {{ form.end_date || '?' }}</dd>
            <dt>Channels</dt><dd>{{ raw.channels || '—' }}</dd>
            <dt>Markets</dt><dd>{{ raw.markets || '—' }}</dd>
            <dt>Tags</dt><dd>{{ raw.tags || '—' }}</dd>
          </dl>
        </div>
      </div>

      <p v-if="error" class="form__error">{{ error }}</p>

      <div class="form__actions">
        <button v-if="step > 0" type="button" class="btn btn--ghost" @click="step--">Back</button>
        <button v-if="step < steps.length - 1" type="submit" class="btn btn--primary">Continue →</button>
        <button v-else type="button" class="btn btn--primary" :disabled="submitting" @click="submit">
          {{ submitting ? 'Creating…' : 'Create campaign' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCampaignsStore } from '@/stores/campaigns'

const router = useRouter()
const campaigns = useCampaignsStore()

const steps = ['Basics', 'Channels & dates', 'Tags & review']
const step = ref(0)
const submitting = ref(false)
const error = ref('')

const form = reactive({ name: '', brand: '', objective: '', start_date: '', end_date: '' })
const raw = reactive({ channels: '', markets: '', tags: '' })

function next() {
  error.value = ''
  if (step.value === 0 && (!form.name || !form.brand)) {
    error.value = 'Name and brand are required.'
    return
  }
  step.value = Math.min(step.value + 1, steps.length - 1)
}

function split(v) {
  return v.split(',').map((s) => s.trim()).filter(Boolean)
}

async function submit() {
  if (!form.name || !form.brand) {
    error.value = 'Name and brand are required.'; step.value = 0; return
  }
  submitting.value = true
  error.value = ''
  try {
    const created = await campaigns.create({
      ...form,
      channels: split(raw.channels),
      markets: split(raw.markets),
      tags: split(raw.tags),
    })
    if (!created?.id) throw new Error('Backend did not return a campaign id.')
    router.push({ name: 'CampaignOverview', params: { campaignId: String(created.id) } })
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || 'Failed to create campaign.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 20px; max-width: 720px; }
.page__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.page__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; }
.page__head p { font-size: 13px; color: var(--co-text-dim); margin-top: 4px; }

.steps { display: flex; gap: 8px; flex-wrap: wrap; }
.step {
  background: transparent; border: 1px solid var(--co-border-2); color: var(--co-text-dim);
  padding: 8px 14px; font-family: var(--co-font-mono); font-size: 12px;
  border-radius: var(--co-radius); cursor: pointer; display: flex; align-items: center; gap: 8px;
}
.step span {
  display: inline-grid; place-items: center;
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--co-surface); font-size: 10px;
}
.step--on { color: var(--co-accent); border-color: var(--co-accent); }
.step--done { color: var(--co-text); }
.step--done span { background: var(--co-accent); color: #000; }

.form {
  background: var(--co-surface); border: 1px solid var(--co-border);
  padding: 24px; display: flex; flex-direction: column; gap: 20px;
}
.form__grid { display: grid; gap: 16px; grid-template-columns: 1fr 1fr; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field span { font-size: 11px; letter-spacing: 0.05em; color: var(--co-text-dim); }
.field--wide { grid-column: 1 / -1; }
.field input {
  background: var(--co-bg); border: 1px solid var(--co-border-2);
  color: var(--co-text); font-family: var(--co-font-mono); font-size: 13px;
  padding: 8px 10px;
}
.field input:focus { outline: none; border-color: var(--co-accent); }

.summary { background: var(--co-bg); padding: 16px; border: 1px solid var(--co-border); }
.summary h3 { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); margin-bottom: 10px; }
.summary dl { display: grid; grid-template-columns: 100px 1fr; gap: 6px 12px; font-size: 12px; }
.summary dt { color: var(--co-text-dim); }
.summary dd { color: var(--co-text); }

.form__error { color: var(--co-danger); font-size: 12px; }
.form__actions { display: flex; gap: 8px; justify-content: flex-end; }

.btn {
  padding: 10px 18px; font-family: var(--co-font-mono); font-size: 12px;
  border-radius: var(--co-radius); cursor: pointer;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
}
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); }
.btn--ghost { background: transparent; }
.btn:disabled { opacity: 0.6; cursor: wait; }

@media (max-width: 600px) {
  .form__grid { grid-template-columns: 1fr; }
}
</style>
