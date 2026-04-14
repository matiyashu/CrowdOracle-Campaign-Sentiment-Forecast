import axios from 'axios'

const BASE = '/api/providers'

export const providersApi = {
  list: () => axios.get(`${BASE}/list`),
  save: (data) => axios.post(`${BASE}/save`, data),
  testConnection: (data) => axios.post(`${BASE}/test-connection`, data),
  patch: (id, data) => axios.patch(`${BASE}/${id}`, data),
  remove: (id) => axios.delete(`${BASE}/${id}`),
  setActive: (providerId) => axios.post(`${BASE}/set-active`, { provider_id: providerId }),
  saveTaskRouting: (routing) => axios.post(`${BASE}/task-routing`, { routing }),
}
