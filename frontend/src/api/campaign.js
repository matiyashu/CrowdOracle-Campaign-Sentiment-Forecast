import axios from 'axios'

const BASE = '/api/campaign'

export const campaignApi = {
  create: (data) => axios.post(`${BASE}/create`, data),
  list: (params) => axios.get(`${BASE}/list`, { params }),
  get: (id) => axios.get(`${BASE}/${id}`),
  patch: (id, data) => axios.patch(`${BASE}/${id}`, data),
  remove: (id) => axios.delete(`${BASE}/${id}`),
}
