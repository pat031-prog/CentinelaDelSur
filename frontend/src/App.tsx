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

  const getPageTitle = () => {
    const path = location.pathname
    if (path === '/') return 'Mission Dashboard'
    if (path === '/regional') return 'Regional Intelligence'
    if (path.startsWith('/country/')) return 'Country Analysis'
    return 'System Status'
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Sidebar Navigation */}
      <aside style={{
        width: 'var(--sidebar-width)',
        background: 'var(--bg-sidebar)',
        color: 'var(--text-on-dark)',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem',
        position: 'fixed',
        top: 0,
        bottom: 0,
        left: 0,
        zIndex: 50
      }}>
        {/* Brand */}
        <div style={{ marginBottom: '3rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '36px', height: '36px',
            background: 'white',
            borderRadius: '8px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--bg-sidebar)',
            fontWeight: 800
          }}>
            A
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>ATALAYA</div>
            <div style={{ fontSize: '0.7rem', opacity: 0.6, fontFamily: 'JetBrains Mono' }}>SYS.V2.0</div>
          </div>
        </div>

        {/* Nav Links */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
          <SidebarLink to="/" icon="⊞" label="Dashboard" active={location.pathname === '/'} />
          <SidebarLink to="/regional" icon="🌐" label="Regional View" active={location.pathname === '/regional'} />
          <div style={{ margin: '1rem 0', height: '1px', background: 'rgba(255,255,255,0.1)' }} />
          <SidebarLink to="#" icon="📁" label="Reports" />
          <SidebarLink to="#" icon="⚙️" label="Settings" />
        </nav>

        {/* Bottom User Profile */}
        <div style={{
          marginTop: 'auto',
          padding: '1rem',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#3b82f6' }} />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Analyst</div>
            <div style={{ fontSize: '0.7rem', opacity: 0.6 }}>lvl.5 Clearance</div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{
        marginLeft: 'var(--sidebar-width)',
        flex: 1,
        padding: '2rem',
        maxWidth: '1600px',
        width: '100%'
      }}>
        {/* Header */}
        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2.5rem',
          height: 'var(--header-height)'
        }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', color: 'var(--text-primary)' }}>
              {getPageTitle()}
            </h1>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--risk-low)' }} />
              System Operational
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            {/* Search */}
            <div style={{
              background: 'white',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '0.5rem 1rem',
              display: 'flex',
              alignItems: 'center',
              width: '300px',
              color: 'var(--text-secondary)'
            }}>
              <span>🔍</span>
              <span style={{ marginLeft: '0.5rem', fontSize: '0.9rem' }}>Search intelligence...</span>
            </div>

            {/* Clock */}
            <div style={{
              fontFamily: 'JetBrains Mono',
              fontSize: '0.9rem',
              fontWeight: 600,
              background: 'var(--bg-sidebar)',
              color: 'white',
              padding: '0.5rem 0.75rem',
              borderRadius: '8px'
            }}>
              {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </header>

        {/* Dynamic Content */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/country/:code" element={<CountryView />} />
          <Route path="/regional" element={<RegionalView />} />
        </Routes>
      </main>
    </div>
  )
}

function SidebarLink({ to, icon, label, active = false }: any) {
  return (
    <Link to={to} style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '0.75rem 1rem',
      borderRadius: '8px',
      color: active ? 'var(--bg-sidebar)' : 'rgba(255,255,255,0.7)',
      background: active ? 'white' : 'transparent',
      textDecoration: 'none',
      fontSize: '0.95rem',
      fontWeight: 500,
      transition: 'all 0.2s ease'
    }}>
      <span style={{ fontSize: '1.1rem' }}>{icon}</span>
      {label}
    </Link>
  )
}

export default App
