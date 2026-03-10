import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Report from './pages/Report'

export default function App() {
  return (
    <div style={{ minHeight: '100vh' }}>
      <nav style={{
        background: '#1e293b',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: '24px',
        borderBottom: '1px solid #334155',
      }}>
        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#f1f5f9' }}>
          📊 Financial Analyzer
        </span>
        <Link to="/" style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Home</Link>
      </nav>

      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report/:ticker" element={<Report />} />
        </Routes>
      </main>
    </div>
  )
}
