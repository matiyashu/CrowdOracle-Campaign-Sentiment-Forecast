import axios from 'axios'

const BASE = '/api/analytics'

export const analyticsApi = {
  uploadMentions: (campaignId, file) => {
    const form = new FormData()
    form.append('campaign_id', campaignId)
    form.append('file', file)
    return axios.post(`${BASE}/mentions/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  uploadPerformance: (campaignId, file) => {
    const form = new FormData()
    form.append('campaign_id', campaignId)
    form.append('file', file)
    return axios.post(`${BASE}/performance/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  dashboard: (campaignId) => axios.get(`${BASE}/dashboard/${campaignId}`),
  keywords: (campaignId) => axios.get(`${BASE}/keywords/${campaignId}`),
  sentiment: (campaignId) => axios.get(`${BASE}/sentiment/${campaignId}`),
  impact: (campaignId) => axios.get(`${BASE}/impact/${campaignId}`),
  generateReport: (data) => axios.post(`${BASE}/report/generate`, data),
  exportDashboardMarkdown: (campaignId) =>
    axios.get(`${BASE}/dashboard/${campaignId}/export.md`, { responseType: 'blob' }),
}
