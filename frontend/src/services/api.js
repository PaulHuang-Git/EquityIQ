const API_BASE = '/api/v1'

export async function analyzeStock(ticker) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function batchAnalyze() {
  const res = await fetch(`${API_BASE}/analyze/batch`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getJobStatus(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getReport(ticker) {
  const res = await fetch(`${API_BASE}/reports/${ticker}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function listReports() {
  const res = await fetch(`${API_BASE}/reports`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getReportHistory(ticker) {
  const res = await fetch(`${API_BASE}/reports/${ticker}/history`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function clearCache(ticker) {
  const res = await fetch(`${API_BASE}/cache/${ticker}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export function connectWS(jobId, onMessage, onClose) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/${jobId}`)
  ws.onmessage = (e) => onMessage(JSON.parse(e.data))
  ws.onclose = () => onClose?.()
  return ws
}
