const RISK_COLORS = {
  Negligible: '#4ade80',
  Low: '#86efac',
  Medium: '#fbbf24',
  High: '#f97316',
  Severe: '#ef4444',
  Unknown: '#64748b',
}

function riskLevel(score) {
  if (score === null || score === undefined) return 'Unknown'
  if (score < 10) return 'Negligible'
  if (score < 20) return 'Low'
  if (score < 30) return 'Medium'
  if (score < 40) return 'High'
  return 'Severe'
}

function ScoreBar({ label, score, maxScore = 50 }) {
  const level = riskLevel(score)
  const color = RISK_COLORS[level]
  const pct = score != null ? Math.min((score / maxScore) * 100, 100) : 0

  return (
    <div style={{ marginBottom: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '0.85rem' }}>
        <span style={{ color: '#94a3b8' }}>{label}</span>
        <span style={{ color }}>
          {score != null ? score.toFixed(1) : 'N/A'} — {level}
        </span>
      </div>
      <div style={{ background: '#0f172a', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '4px', transition: 'width 0.5s' }} />
      </div>
    </div>
  )
}

const styles = {
  card: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '10px',
    padding: '20px',
    marginBottom: '24px',
  },
  title: { fontWeight: 700, color: '#f1f5f9', marginBottom: '16px', fontSize: '1rem' },
  badge: (level) => ({
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '12px',
    background: RISK_COLORS[level] + '22',
    color: RISK_COLORS[level],
    border: `1px solid ${RISK_COLORS[level]}44`,
    fontSize: '0.85rem',
    fontWeight: 600,
    marginBottom: '16px',
  }),
  meta: { fontSize: '0.8rem', color: '#64748b', marginTop: '12px' },
}

export default function ESGScoreCard({ esgData }) {
  if (!esgData) return null

  const {
    total_esg_risk_score,
    environment_score,
    social_score,
    governance_score,
    controversy_level,
    peer_count,
    peer_percentile,
    esg_available,
  } = esgData

  const level = riskLevel(total_esg_risk_score)

  if (!esg_available) {
    return (
      <div style={styles.card}>
        <div style={styles.title}>ESG Risk Assessment</div>
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>ESG data not available for this ticker.</p>
      </div>
    )
  }

  return (
    <div style={styles.card}>
      <div style={styles.title}>ESG Risk Assessment</div>
      <span style={styles.badge(level)}>{level} ESG Risk</span>

      <ScoreBar label="Total ESG Risk Score" score={total_esg_risk_score} />
      <ScoreBar label="Environmental Score" score={environment_score} />
      <ScoreBar label="Social Score" score={social_score} />
      <ScoreBar label="Governance Score" score={governance_score} />

      {controversy_level != null && (
        <div style={{ marginTop: '12px', fontSize: '0.85rem', color: '#94a3b8' }}>
          Controversy Level: <strong style={{ color: controversy_level >= 3 ? '#f97316' : '#94a3b8' }}>
            {controversy_level}/5
          </strong>
        </div>
      )}

      {(peer_count || peer_percentile) && (
        <div style={styles.meta}>
          Peer comparison: {peer_count} peers · percentile {peer_percentile ?? 'N/A'}
        </div>
      )}

      <div style={styles.meta}>
        Source: Yahoo Finance / Sustainalytics — Lower scores = lower ESG risk
      </div>
    </div>
  )
}
