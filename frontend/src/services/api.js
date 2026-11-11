// Thin API client. The base URL is configurable so a separately-hosted frontend
// (Vercel/Netlify) can reach the backend (Render). No secrets are ever bundled here.
const BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

async function request(path, { method = 'GET', body, signal } = {}) {
  let res
  try {
    res = await fetch(`${BASE}/api${path}`, {
      method,
      signal,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch (e) {
    if (e.name === 'AbortError') throw e
    throw new ApiError(0, 'network_error', 'SILO could not reach its server. Check that the backend is running.')
  }
  let data = null
  try { data = await res.json() } catch { /* empty body */ }
  if (!res.ok) {
    const err = data?.error || {}
    throw new ApiError(res.status, err.code || 'http_error', err.message || `Request failed (${res.status}).`, err.details)
  }
  return data
}

const qs = (params) => {
  const p = new URLSearchParams()
  Object.entries(params || {}).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') p.set(k, v) })
  const s = p.toString()
  return s ? `?${s}` : ''
}

export const api = {
  health: (o) => request('/health', o),
  news: (params, o) => request(`/news${qs(params)}`, o),
  article: (id, o) => request(`/news/${id}`, o),
  context: (id, o) => request(`/context-widget/${id}`, o),
  analyze: (body, o) => request('/news/analyze', { method: 'POST', body, ...o }),
  rhetoric: (body, o) => request('/rhetoric/analyze', { method: 'POST', body, ...o }),
  candidates: (o) => request('/candidates', o),
  compare: (a, b, o) => request(`/candidates/compare${qs({ a, b })}`, o),
  finance: (params, o) => request(`/finance-ledger${qs(params)}`, o),
  conflicts: (o) => request('/conflicts', o),
  conflict: (id, o) => request(`/conflicts/${id}`, o),
  methodology: (o) => request('/methodology', o),
  sources: (params, o) => request(`/sources/status${qs(params)}`, o),
}
