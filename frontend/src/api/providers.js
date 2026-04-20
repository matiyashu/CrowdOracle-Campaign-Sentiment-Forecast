import service from './index'

const BASE = '/api/providers'

export const providersApi = {
  list: () => service.get(`${BASE}/list`),
  save: (data) => service.post(`${BASE}/save`, data),
  testConnection: (data) => service.post(`${BASE}/test-connection`, data),
  patch: (id, data) => service.patch(`${BASE}/${id}`, data),
  remove: (id) => service.delete(`${BASE}/${id}`),
  setActive: (providerId) => service.post(`${BASE}/set-active`, { provider_id: providerId }),
  saveTaskRouting: (routing) => service.post(`${BASE}/task-routing`, { routing }),
}
