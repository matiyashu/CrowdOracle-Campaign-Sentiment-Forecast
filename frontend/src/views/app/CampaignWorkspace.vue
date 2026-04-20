<template>
  <section class="wksp">
    <header class="wksp__head">
      <span class="wksp__eyebrow">CAMPAIGN · {{ campaignId }}</span>
      <h1>{{ campaign?.name || 'Campaign workspace' }}</h1>
      <div v-if="campaign" class="wksp__meta">
        <span>{{ campaign.brand }}</span>
        <span v-if="campaign.status">· {{ campaign.status }}</span>
      </div>
    </header>

    <nav class="wksp__tabs">
      <router-link :to="{ name: 'CampaignOverview' }">Overview</router-link>
      <router-link :to="{ name: 'CampaignCreatives' }">Creatives</router-link>
      <router-link :to="{ name: 'CampaignMentions' }">Mentions</router-link>
      <router-link :to="{ name: 'CampaignSentiment' }">Sentiment</router-link>
      <router-link :to="{ name: 'CampaignImpact' }">Impact</router-link>
      <router-link :to="{ name: 'CampaignReport' }">Report</router-link>
    </nav>

    <router-view />
  </section>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useCampaignsStore } from '@/stores/campaigns'

const props = defineProps({ campaignId: { type: String, required: true } })
const campaigns = useCampaignsStore()
const campaign = computed(() => campaigns.current)

onMounted(() => campaigns.load(props.campaignId))
watch(() => props.campaignId, (id) => id && campaigns.load(id))
</script>

<style scoped>
.wksp { display: flex; flex-direction: column; gap: 20px; }
.wksp__eyebrow { font-size: 11px; letter-spacing: 0.15em; color: var(--co-text-dim); }
.wksp__head h1 { font-size: 22px; margin-top: 6px; letter-spacing: -0.01em; }
.wksp__meta { font-size: 13px; color: var(--co-text-dim); margin-top: 4px; display: flex; gap: 8px; }

.wksp__tabs {
  display: flex; gap: 4px; flex-wrap: wrap;
  border-bottom: 1px solid var(--co-border);
}
.wksp__tabs a {
  padding: 10px 14px;
  font-size: 13px; color: var(--co-text-dim);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.wksp__tabs a:hover { color: var(--co-text); }
.wksp__tabs a.router-link-active {
  color: var(--co-accent); border-color: var(--co-accent);
}
</style>
