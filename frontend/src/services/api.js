import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

export async function fetchNews({ category, source, limit = 50, offset = 0 } = {}) {
  const params = { limit, offset }
  if (category && category !== 'All') params.category = category
  if (source && source !== 'All') params.source = source
  const res = await api.get('/news', { params })
  return res.data
}

export async function fetchCategories() {
  const res = await api.get('/categories')
  return res.data
}

export async function fetchSources() {
  const res = await api.get('/sources')
  return res.data
}

export async function fetchMetaCategories() {
  const res = await api.get('/meta/categories')
  return res.data.categories
}

export async function triggerScrape() {
  const res = await api.post('/scrape')
  return res.data
}

export async function checkHealth() {
  const res = await api.get('/health')
  return res.data
}

export default api
