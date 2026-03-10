import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const styles = {
  wrapper: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '10px',
    padding: '32px',
    lineHeight: 1.7,
  },
  downloadBtn: {
    padding: '8px 18px',
    background: '#1d4ed8',
    color: '#fff',
    borderRadius: '6px',
    fontSize: '0.85rem',
    marginBottom: '24px',
    display: 'inline-block',
  },
}

// Minimal markdown component overrides for dark theme
const components = {
  h1: ({ children }) => (
    <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '12px', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#e2e8f0', margin: '24px 0 8px' }}>
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#cbd5e1', margin: '16px 0 6px' }}>
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p style={{ marginBottom: '12px', color: '#94a3b8', fontSize: '0.95rem' }}>{children}</p>
  ),
  table: ({ children }) => (
    <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
        {children}
      </table>
    </div>
  ),
  th: ({ children }) => (
    <th style={{ background: '#0f172a', color: '#94a3b8', padding: '8px 12px', textAlign: 'left', border: '1px solid #334155', fontWeight: 600 }}>
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td style={{ padding: '8px 12px', border: '1px solid #1e293b', color: '#cbd5e1' }}>
      {children}
    </td>
  ),
  blockquote: ({ children }) => (
    <blockquote style={{ borderLeft: '3px solid #2563eb', paddingLeft: '12px', color: '#64748b', fontStyle: 'italic', margin: '12px 0' }}>
      {children}
    </blockquote>
  ),
  code: ({ children }) => (
    <code style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontSize: '0.85em', color: '#7dd3fc' }}>
      {children}
    </code>
  ),
  hr: () => <hr style={{ border: 'none', borderTop: '1px solid #334155', margin: '24px 0' }} />,
  ul: ({ children }) => <ul style={{ paddingLeft: '20px', marginBottom: '12px', color: '#94a3b8' }}>{children}</ul>,
  li: ({ children }) => <li style={{ marginBottom: '4px' }}>{children}</li>,
  strong: ({ children }) => <strong style={{ color: '#e2e8f0' }}>{children}</strong>,
}

export default function ReportViewer({ content, ticker }) {
  function download() {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${ticker}_report.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <button style={styles.downloadBtn} onClick={download}>
        ⬇ Download .md
      </button>
      <div style={styles.wrapper}>
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  )
}
