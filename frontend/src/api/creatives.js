import axios from 'axios'

const BASE = '/api/creatives'

export const creativesApi = {
  upload: (formData) =>
    axios.post(`${BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (assetId) => axios.get(`${BASE}/${assetId}`),
  byCampaign: (campaignId) => axios.get(`${BASE}/by-campaign/${campaignId}`),
  analyze: (assetId) => axios.post(`${BASE}/${assetId}/analyze`),
  batchAnalyze: (assetIds) => axios.post(`${BASE}/batch-analyze`, { asset_ids: assetIds }),
  updateTags: (assetId, tags) => axios.patch(`${BASE}/${assetId}/tags`, { tags }),
}
