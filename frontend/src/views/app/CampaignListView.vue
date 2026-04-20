<template>
  <section class="page">
    <header class="page__head">
      <div>
        <span class="page__eyebrow">WORKSPACE</span>
        <h1>Campaigns</h1>
        <p>Every brief, creative, and mention — organized by campaign.</p>
      </div>
      <router-link to="/app/campaigns/new" class="btn btn--primary">+ New campaign</router-link>
    </header>

    <div class="page__filters">
      <span class="page__filterlabel">STATUS</span>
      <button
        v-for="s in statuses"
        :key="s.value"
        class="chip"
        :class="{ 'chip--on': statusFilter === s.value }"
        @click="statusFilter = s.value"
      >{{ s.label }}</button>
      <input v-model="search" class="page__search" placeholder="Search by name, brand, tag…" />
    </div>

    <div v-if="campaigns.loading && !campaigns.list.length" class="page__skeletons">
      <LoadingSkeleton v-for="i in 3" :key="i" height="120px" />
    </div>

    <ErrorState
      v-else-if="campaigns.error"
      title="Couldn't load campaigns."
      :body="String(campaigns.error?.message || campaigns.error)"
      @retry="reload"
    />

    <EmptyState
      v-else-if="!filtered.length && !search && statusFilter === 'all'"
      title="No campaigns yet."
      body="Start from a demo package or build one from your brief."
    >
      <router-link to="/app/demo" class="btn btn--primary">Try a demo campaign</router-link>
      <router-link to="/app/campaigns/new" class="btn btn--ghost">+ New campaign</router-link>
    </EmptyState>

    <EmptyState
      v-else-if="!filtered.length"
      title="No matches."
      body="Try a different status, or clear the search."
    >
      <button class="btn btn--ghost" @click="resetFilters">Clear filters</button>
    </EmptyState>

    <div v-else class="grid">
      <article
        v-for="c in filtered"
        :key="c.id"
        class="card"
        @click="open(c)"
      >
        <header class="card__head">
          <StatusPill :status="c.status" />
          <span v-if="c.impact_score != null" class="card__impact">
            Impact <strong>{{ c.impact_score }}</strong>
          </span>
        </header>
        <h2 class="card__name">{{ c.name }}</h2>
        <div class="card__brand">{{ c.brand || '—' }}</div>
        <div v-if="c.channels?.length || c.markets?.length" class="card__tags">
          <AppBadge v-for="ch in (c.channels || []).slice(0,3)" :key="'ch-'+ch" tone="neutral">{{ ch }}</AppBadge>
          <AppBadge v-for="m in (c.markets || []).slice(0,2)" :key="'m-'+m" tone="accent">{{ m }}</AppBadge>
        </div>
        <footer class="card__foot">
          <span>{{ c.asset_count ?? 0 }} assets · {{ c.mention_count ?? 0 }} mentions</span>
          <span v-if="c.start_date">{{ c.start_date }} → {{ c.end_date || '…' }}</span>
        </footer>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCampaignsStore } from '@/stores/campaigns'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import StatusPill from '@/components/common/StatusPill.vue'
import AppBadge from '@/components/common/AppBadge.vue'

const router = useRouter()
const campaigns = useCampaignsStore()

const statusFilter = ref('all')
const search = ref('')

const statuses = [
  { value: 'all', label: 'All' },
  { value: 'draft', label: 'Draft' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' },
]

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return campaigns.list.filter((c) => {
    if (statusFilter.value !== 'all' && c.status !== statusFilter.value) return false
    if (!q) return true
    const hay = [c.name, c.brand, ...(c.tags || []), ...(c.channels || []), ...(c.markets || [])]
      .filter(Boolean).join(' ').toLowerCase()
    return hay.includes(q)
  })
})

function open(c) { router.push({ name: 'CampaignOverview', params: { campaignId: String(c.id) } }) }
function resetFilters() { statusFilter.value = 'all'; search.value = '' }
function reload() { campaigns.loadList() }

onMounted(reload)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 24px; }

.page__head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.page__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.page__head h1 { font-size: 26px; margin-top: 6px; letter-spacing: -0.01em; }
.page__head p { color: var(--co-text-dim); font-size: 13px; margin-top: 4px; }

.page__filters { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.page__filterlabel { font-size: 10px; color: var(--co-text-dim); letter-spacing: 0.15em; margin-right: 4px; }
.chip {
  background: transparent; border: 1px solid var(--co-border-2);
  color: var(--co-text-dim); font-family: var(--co-font-mono);
  font-size: 11px; padding: 5px 10px; cursor: pointer; border-radius: var(--co-radius);
}
.chip:hover { color: var(--co-text); }
.chip--on { color: var(--co-accent); border-color: var(--co-accent); }
.page__search {
  flex: 1; min-width: 200px;
  background: var(--co-surface); border: 1px solid var(--co-border-2);
  color: var(--co-text); font-family: var(--co-font-mono);
  padding: 7px 12px; font-size: 12px; border-radius: var(--co-radius);
}
.page__search:focus { outline: none; border-color: var(--co-accent); }

.grid {
  display: grid; gap: 14px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.card {
  background: var(--co-surface);
  border: 1px solid var(--co-border);
  padding: 18px; cursor: pointer;
  display: flex; flex-direction: column; gap: 10px;
  transition: border-color 0.15s;
}
.card:hover { border-color: var(--co-accent); }
.card__head { display: flex; justify-content: space-between; align-items: center; }
.card__impact { font-size: 11px; color: var(--co-text-dim); }
.card__impact strong { color: var(--co-accent); margin-left: 4px; }
.card__name { font-size: 16px; letter-spacing: -0.01em; }
.card__brand { font-size: 12px; color: var(--co-text-dim); }
.card__tags { display: flex; flex-wrap: wrap; gap: 4px; }
.card__foot {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--co-text-mute);
  border-top: 1px solid var(--co-border); padding-top: 10px; margin-top: auto;
}

.btn {
  padding: 8px 16px; font-family: var(--co-font-mono); font-size: 12px;
  border: 1px solid var(--co-border-2); background: var(--co-surface); color: var(--co-text);
  border-radius: var(--co-radius);
}
.btn:hover { border-color: var(--co-accent); color: var(--co-accent); }
.btn--primary { background: var(--co-accent); border-color: var(--co-accent); color: #000; }
.btn--primary:hover { background: var(--co-accent-2); border-color: var(--co-accent-2); color: #000; }
.btn--ghost { background: transparent; }

.page__skeletons { display: flex; flex-direction: column; gap: 12px; }
</style>
