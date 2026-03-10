const STEPS = [
  { key: 'data_collection', label: 'Data Collection' },
  { key: 'financial_analysis', label: 'Financial Analysis' },
  { key: 'esg_scoring', label: 'ESG Scoring' },
  { key: 'report_generation', label: 'Report Generation' },
  { key: 'completed', label: 'Complete' },
]

function stepIndex(step) {
  return STEPS.findIndex((s) => s.key === step)
}

const styles = {
  container: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '10px',
    padding: '20px',
    marginBottom: '16px',
  },
  header: { display: 'flex', justifyContent: 'space-between', marginBottom: '16px' },
  ticker: { fontWeight: 700, fontSize: '1rem', color: '#f1f5f9' },
  status: (step) => ({
    fontSize: '0.8rem',
    padding: '2px 10px',
    borderRadius: '12px',
    background: step === 'completed' ? '#14532d' : step === 'failed' ? '#7f1d1d' : '#1e3a5f',
    color: step === 'completed' ? '#4ade80' : step === 'failed' ? '#f87171' : '#60a5fa',
  }),
  steps: { display: 'flex', gap: '4px', marginBottom: '12px' },
  step: (active, done) => ({
    flex: 1,
    height: '4px',
    borderRadius: '2px',
    background: done ? '#2563eb' : active ? '#60a5fa' : '#334155',
    transition: 'background 0.3s',
  }),
  message: { fontSize: '0.8rem', color: '#64748b', marginTop: '8px' },
}

export default function AnalysisProgress({ ticker, progress }) {
  const { step = '', message = '', progress: pct = 0 } = progress || {}
  const current = stepIndex(step)
  const failed = step === 'failed'

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.ticker}>{ticker}</span>
        <span style={styles.status(step)}>{step || 'pending'}</span>
      </div>

      <div style={styles.steps}>
        {STEPS.slice(0, 4).map((s, i) => (
          <div
            key={s.key}
            style={styles.step(i === current, i < current || step === 'completed')}
            title={s.label}
          />
        ))}
      </div>

      {message && <div style={styles.message}>{message}</div>}
      {failed && (
        <div style={{ ...styles.message, color: '#f87171' }}>
          Analysis failed. Check backend logs.
        </div>
      )}
    </div>
  )
}
