import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import StockSelector from '../components/StockSelector'
import AnalysisProgress from '../components/AnalysisProgress'
import { analyzeStock, listReports, connectWS } from '../services/api'

export default function Home() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])       // [{jobId, ticker, progress}]
  const [recentReports, setRecentReports] = useState([])
  const [loading, setLoading] = useState(false)
  const wsRefs = useRef({})

  useEffect(() => {
    listReports()
      .then(setRecentReports)
      .catch(() => {})
  }, [])

  async function handleAnalyze(tickers) {
    setLoading(true)
    const newJobs = []

    for (const ticker of tickers) {
      try {
        const { job_id } = await analyzeStock(ticker)
        newJobs.push({ jobId: job_id, ticker, progress: null })
      } catch (e) {
        console.error(`Failed to start analysis for ${ticker}:`, e)
      }
    }

    setJobs((prev) => [...newJobs, ...prev])
    setLoading(false)

    // Subscribe to WebSocket progress for each job
    for (const { jobId, ticker } of newJobs) {
      const ws = connectWS(
        jobId,
        (msg) => {
          setJobs((prev) =>
            prev.map((j) => (j.jobId === jobId ? { ...j, progress: msg } : j))
          )
          if (msg.step === 'completed') {
            setRecentReports((prev) => [{ ticker, job_id: jobId, created_at: new Date().toISOString() }, ...prev])
          }
        },
        () => delete wsRefs.current[jobId]
      )
      wsRefs.current[jobId] = ws
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '8px', color: '#f1f5f9' }}>
        Multi-Agent Financial Analyzer
      </h1>
      <p style={{ color: '#64748b', marginBottom: '32px', fontSize: '0.95rem' }}>
        Powered by LangGraph + CrewAI + qwen3.5:35b-a3b
      </p>

      <StockSelector onAnalyze={handleAnalyze} loading={loading} />

      {jobs.length > 0 && (
        <section style={{ marginTop: '24px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px', color: '#94a3b8' }}>
            Active Jobs
          </h2>
          {jobs.map(({ jobId, ticker, progress }) => (
            <div key={jobId}>
              <AnalysisProgress ticker={ticker} progress={progress} />
              {progress?.step === 'completed' && (
                <button
                  onClick={() => navigate(`/report/${ticker}`)}
                  style={{
                    display: 'block',
                    marginTop: '-10px',
                    marginBottom: '16px',
                    padding: '6px 16px',
                    background: '#14532d',
                    color: '#4ade80',
                    border: '1px solid #166534',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                  }}
                >
                  View Report →
                </button>
              )}
            </div>
          ))}
        </section>
      )}

      {recentReports.length > 0 && (
        <section style={{ marginTop: '32px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px', color: '#94a3b8' }}>
            Recent Reports
          </h2>
          <div style={{ display: 'grid', gap: '8px' }}>
            {recentReports.slice(0, 10).map((r, i) => (
              <div
                key={i}
                onClick={() => navigate(`/report/${r.ticker}`)}
                style={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  transition: 'border-color 0.15s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#475569')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#334155')}
              >
                <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{r.ticker}</span>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  {r.created_at ? new Date(r.created_at).toLocaleString() : ''}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
