import { useState, useEffect } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CountryView from './pages/CountryView'
import RegionalView from './pages/RegionalView'

function App() {
  const location = useLocation()

  const navItems = [
    { to: '/', icon: '⊞', label: 'Dashboard' },
    { to: '/regional', icon: '◉', label: 'Regional Scan' },
  ]

  const toolItems = [
    { to: '#', icon: '⬡', label: 'Reports' },
    { to: '#', icon: '⚙', label: 'Settings' },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* ===== SIDEBAR ===== */}
      <aside className="sidebar" style={{
        width: 'var(--sidebar-w)',
        background: 'var(--bg-sidebar)',
        color: 'var(--text-on-dark)',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        zIndex: 100,
        borderRight: '1px solid rgba(255,255,255,0.06)',
      }}>
        {/* Brand */}
        <div style={{
          padding: '1.5rem 1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.625rem',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          <div style={{
            width: 32, height: 32,
            borderRadius: 8,
            background: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.875rem',
            fontWeight: 800,
            color: '#1a1a1a',
          }}>◈</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.01em' }}>ATALAYA</div>
            <div style={{ fontSize: '0.65rem', opacity: 0.4, letterSpacing: '0.08em' }}>INTELLIGENCE SYS</div>
          </div>
        </div>

        {/* General */}
        <div style={{ padding: '1.25rem 0.75rem 0' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 600, opacity: 0.35, letterSpacing: '0.1em', padding: '0 0.5rem', marginBottom: '0.5rem' }}>GENERAL</div>
          {navItems.map(item => (
            <NavLink key={item.to} item={item} active={location.pathname === item.to} />
          ))}
        </div>

        {/* Tools */}
        <div style={{ padding: '1.25rem 0.75rem 0' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 600, opacity: 0.35, letterSpacing: '0.1em', padding: '0 0.5rem', marginBottom: '0.5rem' }}>TOOLS</div>
          {toolItems.map(item => (
            <NavLink key={item.label} item={item} active={false} />
          ))}
        </div>

        {/* Bottom */}
        <div style={{ marginTop: 'auto', padding: '1rem 1.25rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.625rem',
            padding: '0.75rem',
            borderRadius: 10,
            background: 'rgba(255,255,255,0.04)',
          }}>
            <div style={{
              width: 28, height: 28, borderRadius: '50%',
              background: 'linear-gradient(135deg, #C8D5A0, #E8B4A6)',
            }} />
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>Analyst</div>
              <div style={{ fontSize: '0.6rem', opacity: 0.4 }}>Clearance L5</div>
            </div>
          </div>
        </div>
      </aside>

      {/* ===== MAIN ===== */}
      <main className="main-content" style={{
        marginLeft: 'var(--sidebar-w)',
        flex: 1,
        minHeight: '100vh',
      }}>
        {/* Top Bar */}
        <header style={{
          padding: '1.25rem 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-page)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }}>
          {/* Search */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '0.5rem 1rem',
            width: '340px',
          }}>
            <span style={{ opacity: 0.4 }}>🔍</span>
            <input
              type="text"
              placeholder="Search countries, reports..."
              style={{
                border: 'none',
                outline: 'none',
                background: 'transparent',
                fontSize: '0.875rem',
                fontFamily: 'inherit',
                color: 'var(--text-primary)',
                width: '100%',
              }}
            />
          </div>

          {/* Filter tabs (like Intelly) */}
          <div style={{ display: 'flex', gap: '0.25rem' }}>
            {['All', 'Critical', 'Watchlist', 'Stable'].map((tab, i) => (
              <button key={tab} className={i === 0 ? 'btn btn--primary' : 'pill'} style={{
                ...(i === 0 ? { padding: '6px 14px', fontSize: '0.8rem' } : { cursor: 'pointer', fontSize: '0.8rem' }),
              }}>
                {tab}
              </button>
            ))}
          </div>

          {/* Time + Notifications */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Clock />
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              border: '1px solid var(--border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.85rem', cursor: 'pointer',
            }}>🔔</div>
          </div>
        </header>

        {/* Page Content */}
        <div style={{ padding: '2rem' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/country/:code" element={<CountryView />} />
            <Route path="/regional" element={<RegionalView />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

function NavLink({ item, active }: { item: { to: string; icon: string; label: string }; active: boolean }) {
  return (
    <Link to={item.to} style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.625rem',
      padding: '0.625rem 0.75rem',
      borderRadius: 8,
      color: active ? '#1a1a1a' : 'rgba(255,255,255,0.6)',
      background: active ? '#fff' : 'transparent',
      fontWeight: active ? 600 : 400,
      fontSize: '0.875rem',
      marginBottom: '2px',
      transition: 'all 0.15s ease',
    }}>
      <span style={{ fontSize: '1rem', width: 20, textAlign: 'center' }}>{item.icon}</span>
      {item.label}
    </Link>
  )
}

function Clock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return (
    <span style={{
      fontSize: '0.8rem',
      fontWeight: 600,
      color: 'var(--text-secondary)',
      letterSpacing: '0.02em',
    }}>
      {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
    </span>
  )
}

export default App
