import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Country, Alert } from '../types'
import MarketTicker from '../components/MarketTicker'

export default function Dashboard() {
  const [countries, setCountries] = useState<Country[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [c, a] = await Promise.all([api.getCountries(), api.getAlerts()])
        setCountries(c || [])
        setAlerts(a?.alerts || [])
      } catch (e) {
        console.error("Dashboard load failed:", e)
        setCountries([])
        setAlerts([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return (
    <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>
      Cargando sistema...
    </div>
  )

  const critical = countries.filter(c => c.current_risk_score >= 70)
  const watchlist = countries.filter(c => c.current_risk_score >= 40 && c.current_risk_score < 70)
  const avgRisk = countries.length
    ? countries.reduce((a, c) => a + c.current_risk_score, 0) / countries.length
    : 0

  return (
    <div className="fade-in">

      {/* ===== TOP ROW: Hero + Metrics ===== */}
      <div className="grid-dashboard">

        {/* HERO CARD */}
        <div className="grid-card span-2" style={{ padding: '2rem' }}>
          <div className="t-label" style={{ marginBottom: '0.75rem' }}>Sala de Situación</div>
          <h1 className="t-display t-xl">Panel de<br />Control</h1>
        </div>

        {/* DESCRIPTION */}
        <div className="grid-card span-2" style={{ display: 'flex', alignItems: 'flex-end', padding: '2rem' }}>
          <p style={{ fontSize: '0.85rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
            Monitoreo en tiempo real de <strong style={{ color: 'var(--text-primary)' }}>{countries.length}</strong> entidades
            soberanas. Ciclo de inteligencia activo.
          </p>
        </div>

        {/* METRIC CARDS */}
        <MetricCard label="Entidades" value={String(countries.length)} />
        <MetricCard label="Críticos" value={String(critical.length)} color="orange" />
        <MetricCard label="Vigilancia" value={String(watchlist.length)} color="sage" />
        <MetricCard label="Índice Regional" value={avgRisk.toFixed(1)} />
      </div>

      {/* ===== MAIN BODY: Matrix + Cable ===== */}
      <MarketTicker />
      <div className="grid-dashboard" style={{ marginTop: '0' }}>

        {/* RISK MATRIX */}
        <div className="grid-card span-3" style={{ padding: 0, overflow: 'hidden' }}>
          {/* Header */}
          <div style={{
            padding: '1rem 1.5rem',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span className="t-display" style={{ fontSize: '1.1rem' }}>Matriz de Riesgo</span>
            <span className="t-label">{countries.length} entidades</span>
          </div>

          {/* Table Header */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '60px 1fr 80px 120px',
            padding: '0.6rem 1.5rem',
            fontSize: '0.65rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--text-dim)',
            borderBottom: '1px solid var(--border-light)',
          }}>
            <div>ISO</div>
            <div>Entidad</div>
            <div style={{ textAlign: 'center' }}>Score</div>
            <div style={{ textAlign: 'right' }}>Estado</div>
          </div>

          {/* Rows */}
          {countries.map(c => (
            <Link key={c.code} to={`/country/${c.code}`} style={{
              display: 'grid',
              gridTemplateColumns: '60px 1fr 80px 120px',
              padding: '0.85rem 1.5rem',
              borderBottom: '1px solid var(--border-light)',
              alignItems: 'center',
              textDecoration: 'none',
              color: 'inherit',
              transition: 'background 0.1s',
            }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-card-hover)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{ fontFamily: 'var(--font-data)', fontWeight: 600, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {c.code}
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{c.name}</div>
              <div style={{
                textAlign: 'center',
                fontFamily: 'var(--font-data)',
                fontWeight: 700,
                fontSize: '1rem',
                color: scoreColor(c.current_risk_score)
              }}>
                {c.current_risk_score.toFixed(0)}
              </div>
              <div style={{ textAlign: 'right' }}>
                <RiskPill level={c.current_risk_level} />
              </div>
            </Link>
          ))}
        </div>

        {/* NEWS CABLE */}
        <div className="grid-card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{
            padding: '1rem 1.25rem',
            borderBottom: '1px solid var(--border-color)',
          }}>
            <span className="t-display" style={{ fontSize: '1.1rem' }}>Cable</span>
          </div>

          <div>
            {alerts.slice(0, 8).map(a => (
              <div key={a.id} style={{
                padding: '1rem 1.25rem',
                borderBottom: '1px solid var(--border-light)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{
                    fontFamily: 'var(--font-data)',
                    fontSize: '0.6rem',
                    fontWeight: 700,
                    background: 'var(--accent)',
                    color: '#FFF',
                    padding: '1px 6px',
                    borderRadius: '2px'
                  }}>{a.country_code}</span>
                  <span style={{ fontFamily: 'var(--font-data)', fontSize: '0.6rem', color: 'var(--text-dim)' }}>
                    {new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', lineHeight: 1.4, fontWeight: 500 }}>{a.title}</p>
                {a.editorial && (
                  <p style={{
                    marginTop: '0.3rem',
                    fontSize: '0.75rem',
                    fontStyle: 'italic',
                    color: 'var(--text-muted)',
                    lineHeight: 1.4
                  }}>
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

/* ===== METRIC CARD ===== */
function MetricCard({ label, value, color }: { label: string, value: string, color?: 'orange' | 'sage' }) {
  const cardClass = color === 'orange' ? 'grid-card orange' : color === 'sage' ? 'grid-card sage' : 'grid-card'
  return (
    <div className={cardClass}>
      <div style={{
        fontSize: '0.6rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        opacity: 0.7,
        marginBottom: '0.5rem'
      }}>{label}</div>
      <div className="t-display t-lg">{value}</div>
    </div>
  )
}

/* ===== RISK PILL ===== */
function RiskPill({ level }: { level: string }) {
  const colorMap: Record<string, string> = {
    CRITICAL: 'var(--risk-critical)',
    HIGH: 'var(--risk-high)',
    MEDIUM: 'var(--risk-medium)',
    LOW: 'var(--risk-low)',
  }
  const color = colorMap[level] || 'var(--text-muted)'

  return (
    <span style={{
      fontSize: '0.6rem',
      fontWeight: 700,
      fontFamily: 'var(--font-data)',
      color: color,
      border: `1px solid ${color}`,
      padding: '2px 8px',
      borderRadius: 'var(--radius-xs)',
      textTransform: 'uppercase',
      letterSpacing: '0.03em'
    }}>
      {level}
    </span>
  )
}

function scoreColor(score: number): string {
  if (score >= 70) return 'var(--risk-critical)'
  if (score >= 50) return 'var(--risk-high)'
  if (score >= 30) return 'var(--risk-medium)'
  return 'var(--risk-low)'
}
