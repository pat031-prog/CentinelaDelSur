import { useState, useEffect } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CountryView from './pages/CountryView'
import RegionalView from './pages/RegionalView'

function App() {
  const location = useLocation()

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-page)' }}>
      {/* ===== THE ARCHIVE SIDEBAR (File Stack) ===== */}
      <aside style={{
        width: 'var(--sidebar-width)',
        background: 'var(--bg-sidebar)',
        color: 'var(--text-inverse)',
        display: 'flex',
        flexDirection: 'column',
        borderRight: 'var(--border-width) solid var(--border-color)',
        height: '100vh',
        position: 'fixed',
        zIndex: 100
      }}>
        {/* Brand */}
        <div style={{ padding: '2rem 1.5rem', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>
          <h1 className="type-display" style={{ fontSize: '2rem', color: '#FFF', marginBottom: '0.25rem' }}>ATALAYA</h1>
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#888' }}>INTELLIGENCE UNIT</div>
        </div>

        {/* Navigation Folders */}
        <nav style={{ flex: 1, padding: '1rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <FolderTab to="/" label="SALA DE SITUACIÓN" index="001" active={location.pathname === '/'} />
          <FolderTab to="/regional" label="MAPA DE CALOR" index="002" active={location.pathname === '/regional'} />
          <FolderTab to="#" label="REPORTES (LOCKED)" index="003" active={false} disabled />
          <FolderTab to="#" label="FUENTES" index="004" active={false} disabled />
        </nav>

        {/* System Footer */}
        <div style={{ padding: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.2)' }}>
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#444' }}>
            <div>SYSTEM: V2.1.0</div>
            <div>CONN: SECURE</div>
          </div>
        </div>
      </aside>

      {/* ===== MAIN CONTENT ===== */}
      <main style={{ marginLeft: 'var(--sidebar-width)', flex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

        {/* MASTHEAD HEADER */}
        <header style={{
          height: 'var(--header-height)',
          borderBottom: 'var(--border-width) solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 2rem',
          background: 'var(--bg-page)',
          position: 'sticky', top: 0, zIndex: 90
        }}>
          {/* Breadcrumbs / Search */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span className="type-mono" style={{ fontSize: '1.5rem' }}>↗</span>
            <input
              type="text"
              placeholder="BUSCAR EXPEDIENTE..."
              className="type-mono"
              style={{
                background: 'transparent',
                border: 'none',
                borderBottom: '2px solid black',
                width: '300px',
                padding: '0.25rem',
                fontSize: '0.9rem',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
          </div>

          <Clock />
        </header>

        {/* VIEWPORT */}
        <div style={{ flex: 1, position: 'relative' }}>
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

/* ===== FOLDER TAB COMPONENT (The "File") ===== */
function FolderTab({ to, label, index, active, disabled = false }: { to: string, label: string, index: string, active: boolean, disabled?: boolean }) {
  return (
    <Link to={to} style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '1rem 1.25rem',
      background: active ? '#F2EFE9' : '#111', // Invert when active
      color: active ? '#000' : (disabled ? '#333' : '#AAA'),
      border: '1px solid',
      borderColor: active ? '#000' : '#333',
      transform: active ? 'translateX(10px)' : 'none', // Pop out effect
      transition: 'all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      pointerEvents: disabled ? 'none' : 'auto',
      clipPath: 'polygon(0% 0%, 92% 0%, 100% 20%, 100% 100%, 0% 100%)', // Folder cut
      marginBottom: '-4px' // Stack effect
    }}>
      <span className="type-mono" style={{ fontWeight: 700, fontSize: '0.85rem' }}>{label}</span>
      <span className="type-mono" style={{ fontSize: '0.7rem', opacity: 0.5 }}>{index}</span>
    </Link>
  )
}

function Clock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t) }, [])
  return (
    <div className="type-mono" style={{ border: '1px solid black', padding: '0.5rem 1rem', background: '#FFF' }}>
      {time.toLocaleTimeString()} <span style={{ fontSize: '0.7em' }}>ART</span>
    </div>
  )
}

export default App
