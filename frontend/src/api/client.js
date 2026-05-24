import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 20000,
})

export async function analyzeRisk({ userId, message }) {
  const { data } = await api.post('/api/analyze', { user_id: userId, message })
  return data
}

export async function getAlerts(userId) {
  const { data } = await api.get('/api/alerts', { params: userId ? { user_id: userId } : {} })
  return data
}

export async function getHealth() {
  const { data } = await api.get('/health')
  return data
}

export async function getRiskPreview(params) {
  const { data } = await api.get('/api/risk/preview', { params })
  return data
}

export function createActivityStream() {
  const base = import.meta.env.VITE_API_BASE_URL || ''
  return new EventSource(`${base}/api/activity/stream`)
}

