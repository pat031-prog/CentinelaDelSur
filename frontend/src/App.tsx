import { useState, useEffect } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CountryView from './pages/CountryView'
import RegionalView from './pages/RegionalView'

function App() {
  const location = useLocation()

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>

      {/* ===== SIDEBAR ===== */}
      <aside className="sidebar" style={{
        width: 'var(--sidebar-width)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'fixed',
        zIndex: 100,
        borderRight: '1px solid var(--border-color)'
      }}>
        {/* Brand */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <h1 className="t-display" style={{ fontSize: '1.4rem', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            ATALAYA
          </h1>
          <div style={{
            fontSize: '0.6rem',
            fontWeight: 600,
            color: 'var(--text-dim)',
            textTransform: 'uppercase',
            letterSpacing: '0.15em',
            marginTop: '0.15rem'
          }}>Intelligence</div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <NavItem to="/" label="Sala de Situación" tag="( a )" active={location.pathname === '/'} />
          <NavItem to="/regional" label="Mapa de Calor" tag="( b )" active={location.pathname === '/regional'} />
          <NavItem to="#" label="Reportes" tag="( c )" active={false} disabled />
          <NavItem to="#" label="Fuentes" tag="( d )" active={false} disabled />
        </nav>

        {/* Footer */}
        <div style={{ padding: '1.25rem', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.6rem', color: 'var(--text-dim)', lineHeight: 1.8, fontFamily: 'var(--font-data)' }}>
            <div>SYS v2.1.0</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <div style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--risk-low)' }} />
              ONLINE
            </div>
          </div>
        </div>
      </aside>

      {/* ===== MAIN ===== */}
      <main className="main-content" style={{
        marginLeft: 'var(--sidebar-width)',
        flex: 1,
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column'
      }}>

        {/* HEADER */}
        <header style={{
          height: 'var(--header-height)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1.5rem',
          background: 'var(--bg-secondary)',
          position: 'sticky',
          top: 0,
          zIndex: 90
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.9rem' }}>⌕</span>
            <input
              type="text"
              placeholder="Buscar expediente..."
              style={{
                background: 'transparent',
                border: 'none',
                width: '250px',
                fontSize: '0.8rem',
                color: 'var(--text-secondary)',
                outline: 'none',
                fontFamily: 'var(--font-body)'
              }}
            />
          </div>
          <Clock />
        </header>

        {/* CONTENT */}
        <div style={{ flex: 1, padding: '6px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/country/:code" element={<CountryView />} />
            <Route path="/regional" element={<RegionalView />} />
          </Routes>
        </div>
      </main>

      {/* BOTTOM NAV (Mobile) */}
      <div className="bottom-nav">
        <Link to="/" className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
          <span style={{ fontSize: '1rem' }}>◉</span>
          <span>Panel</span>
        </Link>
        <Link to="/regional" className={`nav-item ${location.pathname === '/regional' ? 'active' : ''}`}>
          <span style={{ fontSize: '1rem' }}>◎</span>
          <span>Regional</span>
        </Link>
      </div>
    </div>
  )
}

/* ===== NAV ITEM (Apollo-style with tags) ===== */
function NavItem({ to, label, tag, active, disabled = false }: {
  to: string, label: string, tag: string, active: boolean, disabled?: boolean
}) {
  return (
    <Link to={to} style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.7rem 0.85rem',
      background: active ? 'var(--bg-card)' : 'transparent',
      color: active ? 'var(--text-primary)' : (disabled ? 'var(--text-dim)' : 'var(--text-secondary)'),
      borderRadius: 'var(--radius-sm)',
      fontSize: '0.8rem',
      fontWeight: active ? 600 : 400,
      transition: 'all 0.12s ease',
      pointerEvents: disabled ? 'none' : 'auto',
    }}>
      <span>{label}</span>
      <span style={{
        fontFamily: 'var(--font-data)',
        fontSize: '0.65rem',
        color: active ? 'var(--text-muted)' : 'var(--text-dim)',
        letterSpacing: '0.05em'
      }}>{tag}</span>
    </Link>
  )
}

function Clock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t) }, [])
  return (
    <div style={{
      fontFamily: 'var(--font-data)',
      fontSize: '0.75rem',
      color: 'var(--text-muted)',
      background: 'var(--bg-card)',
      padding: '0.3rem 0.75rem',
      borderRadius: 'var(--radius-xs)',
    }}>
      {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </div>
  )
}

export default App
