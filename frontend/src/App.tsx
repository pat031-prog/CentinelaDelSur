import { useState, useEffect } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CountryView from './pages/CountryView'
import RegionalView from './pages/RegionalView'

function App() {
  const [time, setTime] = useState(new Date())
  const location = useLocation()

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const getBreadcrumb = () => {
    const path = location.pathname
    if (path === '/') return 'DASHBOARD'
    if (path.startsWith('/country/')) return 'COUNTRY INTELLIGENCE'
    if (path === '/regional') return 'REGIONAL OVERVIEW'
    return path.toUpperCase()
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navigation Bar */}
      <nav style={{
        height: 'var(--nav-height)',
        background: 'rgba(5, 9, 16, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid var(--border)',
        padding: '0 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
      }}>
        {/* Left: Logo & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <Link to="/" style={{
            fontFamily: 'JetBrains Mono',
            fontSize: '1.25rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            letterSpacing: '0.15em',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            textShadow: '0 0 10px rgba(56, 189, 248, 0.3)',
          }}>
            <div style={{
              width: '24px',
              height: '24px',
              border: '2px solid var(--accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <div style={{ width: '8px', height: '8px', background: 'var(--accent)' }} />
            </div>
            ATALAYA
          </Link>

          <div style={{ width: '1px', height: '24px', background: 'var(--border)' }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', fontFamily: 'JetBrains Mono', color: 'var(--text-muted)' }}>
            <div className="status-dot" />
            <span>SYSTEM OPERATIONAL</span>
          </div>
        </div>

        {/* Center: Breadcrumbs */}
        <div style={{
          position: 'absolute',
          left: '50%',
          transform: 'translateX(-50%)',
          fontFamily: 'JetBrains Mono',
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          letterSpacing: '0.1em',
        }}>
           // {getBreadcrumb()}
        </div>

        {/* Right: Clock & Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem', fontWeight: 500 }}>
            <Link to="/" style={{
              color: location.pathname === '/' ? 'var(--accent)' : 'var(--text-secondary)',
              textShadow: location.pathname === '/' ? '0 0 8px var(--accent-glow)' : 'none'
            }}>DASHBOARD</Link>
            <Link to="/regional" style={{
              color: location.pathname === '/regional' ? 'var(--accent)' : 'var(--text-secondary)',
              textShadow: location.pathname === '/regional' ? '0 0 8px var(--accent-glow)' : 'none'
            }}>REGIONAL</Link>
          </div>

          <div style={{ width: '1px', height: '24px', background: 'var(--border)' }} />

          <div style={{
            fontFamily: 'JetBrains Mono',
            fontSize: '0.85rem',
            color: 'var(--accent)',
            background: 'var(--accent-glow)',
            padding: '0.25rem 0.75rem',
            borderRadius: '4px',
            border: '1px solid var(--border)'
          }}>
            {time.toISOString().slice(11, 19)} UTC
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main style={{
        flex: 1,
        padding: 'calc(var(--nav-height) + 2rem) 2rem 2rem',
        maxWidth: '1600px',
        margin: '0 auto',
        width: '100%'
      }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/country/:code" element={<CountryView />} />
          <Route path="/regional" element={<RegionalView />} />
        </Routes>
      </main>

      {/* Ambient Grid Background */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
          linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
        pointerEvents: 'none',
        zIndex: -1,
      }} />
    </div>
  )
}

export default App
