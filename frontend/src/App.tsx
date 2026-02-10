import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CountryView from './pages/CountryView'
import RegionalView from './pages/RegionalView'

function App() {
  return (
    <div style={{ minHeight: '100vh' }}>
      <nav style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border)',
        padding: '1rem 2rem',
        display: 'flex',
        alignItems: 'center',
        gap: '2rem',
      }}>
        <Link to="/" style={{
          fontSize: '1.5rem',
          fontWeight: 'bold',
          color: 'var(--text-primary)',
          textDecoration: 'none',
          letterSpacing: '0.1em',
        }}>
          ATALAYA
        </Link>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Systemic Crisis Detection
        </span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '1.5rem' }}>
          <Link to="/">Dashboard</Link>
          <Link to="/regional">Regional</Link>
        </div>
      </nav>

      <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/country/:code" element={<CountryView />} />
          <Route path="/regional" element={<RegionalView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
