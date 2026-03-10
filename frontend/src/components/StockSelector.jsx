import { useState } from 'react'

const DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'XOM']

const styles = {
  container: { marginBottom: '24px' },
  label: { display: 'block', marginBottom: '8px', color: '#94a3b8', fontSize: '0.875rem', fontWeight: 500 },
  chips: { display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' },
  chip: (selected) => ({
    padding: '6px 14px',
    borderRadius: '20px',
    border: '1px solid',
    borderColor: selected ? '#3b82f6' : '#334155',
    background: selected ? '#1d4ed8' : '#1e293b',
    color: selected ? '#fff' : '#94a3b8',
    fontSize: '0.85rem',
    cursor: 'pointer',
    transition: 'all 0.15s',
  }),
  customRow: { display: 'flex', gap: '8px', marginTop: '8px' },
  input: {
    flex: 1,
    padding: '8px 12px',
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '6px',
    color: '#e2e8f0',
    fontSize: '0.9rem',
  },
  addBtn: {
    padding: '8px 16px',
    background: '#334155',
    color: '#e2e8f0',
    borderRadius: '6px',
    fontSize: '0.85rem',
  },
  analyzeBtn: (disabled) => ({
    width: '100%',
    padding: '12px',
    marginTop: '16px',
    background: disabled ? '#334155' : '#2563eb',
    color: disabled ? '#64748b' : '#fff',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'background 0.2s',
  }),
}

export default function StockSelector({ onAnalyze, loading }) {
  const [selected, setSelected] = useState(['AAPL'])
  const [custom, setCustom] = useState('')

  function toggle(ticker) {
    setSelected((prev) =>
      prev.includes(ticker) ? prev.filter((t) => t !== ticker) : [...prev, ticker]
    )
  }

  function addCustom() {
    const t = custom.trim().toUpperCase()
    if (t && !selected.includes(t)) {
      setSelected((prev) => [...prev, t])
    }
    setCustom('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') addCustom()
  }

  return (
    <div style={styles.container}>
      <label style={styles.label}>Select stocks to analyze</label>
      <div style={styles.chips}>
        {DEFAULT_TICKERS.map((t) => (
          <button key={t} style={styles.chip(selected.includes(t))} onClick={() => toggle(t)}>
            {t}
          </button>
        ))}
        {selected.filter((t) => !DEFAULT_TICKERS.includes(t)).map((t) => (
          <button key={t} style={styles.chip(true)} onClick={() => toggle(t)}>
            {t} ×
          </button>
        ))}
      </div>

      <div style={styles.customRow}>
        <input
          style={styles.input}
          placeholder="Add custom ticker (e.g. NVDA)"
          value={custom}
          onChange={(e) => setCustom(e.target.value.toUpperCase())}
          onKeyDown={handleKeyDown}
        />
        <button style={styles.addBtn} onClick={addCustom}>Add</button>
      </div>

      <button
        style={styles.analyzeBtn(loading || selected.length === 0)}
        disabled={loading || selected.length === 0}
        onClick={() => onAnalyze(selected)}
      >
        {loading ? 'Analyzing…' : `Analyze ${selected.length} stock${selected.length !== 1 ? 's' : ''}`}
      </button>
    </div>
  )
}
