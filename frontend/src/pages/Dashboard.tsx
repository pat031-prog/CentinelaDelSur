import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Country, Alert } from '../types'

export default function Dashboard() {
  const [countries, setCountries] = useState<Country[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [c, a] = await Promise.all([api.getCountries(), api.getAlerts()])
        setCountries(c)
        setAlerts(a.alerts || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="type-mono" style={{ padding: '2rem' }}>LOADING SYSTEM...</div>

  const critical = countries.filter(c => c.current_risk_score >= 70)
  const watchlist = countries.filter(c => c.current_risk_score >= 40 && c.current_risk_score < 70)
  const avgRisk = countries.length
    ? countries.reduce((a, c) => a + c.current_risk_score, 0) / countries.length
    : 0

  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto' }}>

      {/* ===== HERO SECTION ===== */}
      <div className="brutalist-grid" style={{ marginBottom: '4rem' }}>
        <div className="grid-cell double-width">
          <h2 className="type-mono" style={{ fontSize: '0.8rem', color: '#666', marginBottom: '1rem' }}>SALA DE SITUACIÓN</h2>
          <h1 className="type-display text-xl">PANEL DE CONTROL</h1>
        </div>
        <div className="grid-cell double-width">
          <p className="type-mono" style={{ fontSize: '0.9rem', lineHeight: 1.6, maxWidth: '80%' }}>
            MONITOREO EN TIEMPO REAL DE {countries.length} ENTIDADES SOBERANAS.
            CICLO DE INTELIGENCIA ACTIVO.
          </p>
        </div>

        {/* KEY METRICS */}
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>ENTIDADES</div>
          <div className="type-display text-lg">{countries.length}</div>
        </div>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>CRÍTICOS</div>
          <div className="type-display text-lg" style={{ color: critical.length > 0 ? 'var(--risk-critical)' : 'inherit' }}>
            {critical.length}
          </div>
        </div>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>VIGILANCIA</div>
          <div className="type-display text-lg">{watchlist.length}</div>
        </div>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>INDICE REGIONAL</div>
          <div className="type-display text-lg">{avgRisk.toFixed(1)}</div>
        </div>
      </div>

      {/* ===== MAIN CONTENT GRID ===== */}
      <div className="brutalist-grid">

        {/* COL 1-3: MATRIX DE RIESGO */}
        <div className="grid-cell" style={{ gridColumn: 'span 3', padding: 0 }}>
          <div style={{ padding: '1.5rem', borderBottom: 'var(--border-width) solid var(--border-color)' }}>
            <h3 className="type-display text-md">MATRIZ DE RIESGO</h3>
          </div>

          {/* TABLE HEADER */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '80px 1fr 100px 150px',
            padding: '1rem 1.5rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            borderBottom: '1px solid var(--border-light)'
          }}>
            <div>ISO</div>
            <div>ENTIDAD</div>
            <div style={{ textAlign: 'center' }}>SCORE</div>
            <div style={{ textAlign: 'right' }}>ESTADO</div>
          </div>

          {/* ROWS */}
          {countries.map(c => (
            <Link key={c.code} to={`/country/${c.code}`} style={{
              display: 'grid',
              gridTemplateColumns: '80px 1fr 100px 150px',
              padding: '1.25rem 1.5rem',
              borderBottom: '1px solid var(--border-light)',
              alignItems: 'center',
              textDecoration: 'none',
              color: 'inherit'
            }} className="hover:bg-white">
              <div className="type-mono" style={{ fontWeight: 700 }}>{c.code}</div>
              <div className="type-display" style={{ fontSize: '1.1rem' }}>{c.name}</div>
              <div className="type-mono" style={{ textAlign: 'center', fontWeight: 700, fontSize: '1.1rem' }}>
                {c.current_risk_score.toFixed(0)}
              </div>
              <div style={{ textAlign: 'right' }}>
                <RiskTag level={c.current_risk_level} />
              </div>
            </Link>
          ))}
        </div>

        {/* COL 4: CABLE DE NOTICIAS */}
        <div className="grid-cell" style={{ gridColumn: 'span 1', padding: 0, borderLeft: 'var(--border-width) solid var(--border-color)' }}>
          <div style={{ padding: '1.5rem', borderBottom: 'var(--border-width) solid var(--border-color)' }}>
            <h3 className="type-display text-md">CABLE</h3>
          </div>
          <div>
            {alerts.slice(0, 8).map(a => (
              <div key={a.id} style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-light)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span className="type-mono" style={{ fontSize: '0.7rem', fontWeight: 700 }}>{a.country_code}</span>
                  <span className="type-mono" style={{ fontSize: '0.7rem', color: '#888' }}>
                    {new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.4, fontWeight: 500 }}>{a.title}</p>
                {a.editorial && (
                  <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', fontStyle: 'italic', color: '#555', fontFamily: 'serif' }}>
                    "{a.editorial}"
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}

function RiskTag({ level }: { level: string }) {
  let color = '#000'
  if (level === 'CRITICAL') color = 'var(--risk-critical)'
  if (level === 'HIGH') color = 'var(--risk-high)'
  if (level === 'MEDIUM') color = 'var(--risk-medium)'
  if (level === 'LOW') color = 'var(--risk-low)'

  return (
    <span className="type-mono" style={{
      fontSize: '0.7rem',
      fontWeight: 700,
      color: color,
      border: `1px solid ${color}`,
      padding: '2px 6px'
    }}>
      {level}
    </span>
  )
}
