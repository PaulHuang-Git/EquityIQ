import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReportViewer from '../components/ReportViewer'
import ESGScoreCard from '../components/ESGScoreCard'
import { getReport } from '../services/api'

export default function Report() {
  const { ticker } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getReport(ticker)
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [ticker])

  // Extract ESG data from report content (heuristic parse from report JSON fields)
  // The ESG data is embedded in the markdown so we parse the score card separately
  const esgData = report?.esg_data || null

  if (loading) {
    return (
      <div style={{ color: '#64748b', padding: '40px 0' }}>Loading report for {ticker}…</div>
    )
  }

  if (error) {
    return (
      <div>
        <button onClick={() => navigate('/')} style={{ color: '#60a5fa', background: 'none', fontSize: '0.9rem', marginBottom: '16px' }}>
          ← Back
        </button>
        <div style={{ background: '#7f1d1d', border: '1px solid #991b1b', borderRadius: '8px', padding: '16px', color: '#fca5a5' }}>
          No report found for <strong>{ticker}</strong>. Run an analysis first.
        </div>
      </div>
    )
  }

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        style={{ color: '#60a5fa', background: 'none', fontSize: '0.9rem', marginBottom: '20px', display: 'block' }}
      >
        ← Back to Home
      </button>

      {esgData && <ESGScoreCard esgData={esgData} />}

      {report?.report_content ? (
        <ReportViewer content={report.report_content} ticker={ticker} />
      ) : (
        <div style={{ color: '#64748b' }}>Report content unavailable.</div>
      )}
    </div>
  )
}
