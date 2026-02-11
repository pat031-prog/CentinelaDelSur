import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import RiskGauge from '../components/RiskGauge'

export default function RegionalView() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const res = await api.getRegionalOverview()
        setData(res)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return (
    <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Iniciando escaneo regional...</div>
  )

  if (!data) return (
    <div style={{ padding: '3rem', color: 'var(--risk-critical)' }}>Región no disponible.</div>
  )

  const scoreToLevel = (s: number) => {
    if (s >= 85) return 'black' as const
    if (s >= 70) return 'red' as const
    if (s >= 50) return 'orange' as const
    if (s >= 30) return 'yellow' as const
    return 'green' as const
  }

  const dist = data.risk_distribution || {}
  const distColors: Record<string, string> = {
    green: 'var(--risk-low)',
    yellow: 'var(--risk-medium)',
    orange: 'var(--risk-high)',
    red: 'var(--risk-critical)',
    black: 'var(--text-primary)',
  }
  const levelLabels: Record<string, string> = {
    green: 'Estable', yellow: 'Vigilancia', orange: 'Elevado', red: 'Crítico', black: 'Colapso',
  }
  const cardColors: Record<string, string> = {
    green: 'sage', yellow: '', orange: 'orange', red: 'orange', black: 'dark',
  }

  return (
    <div className="fade-in">

      {/* ===== HERO ===== */}
      <div className="grid-dashboard">
        <div className="grid-card span-3" style={{ padding: '2.5rem' }}>
          <div className="t-label" style={{ marginBottom: '0.5rem' }}>Inteligencia Regional</div>
          <h1 className="t-display" style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>
            Radar Hemisférico
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '500px', lineHeight: 1.5 }}>
            Escaneo de <strong style={{ color: 'var(--text-primary)' }}>{data.total_countries}</strong> entidades soberanas.
            Índice de fragilidad: <strong style={{ color: 'var(--accent)' }}>{data.regional_risk_score?.toFixed(1)}</strong>
          </p>
        </div>

        <div className="grid-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
          <div className="t-label" style={{ marginBottom: '0.75rem' }}>Amenaza</div>
          <RiskGauge
            score={data.regional_risk_score || 0}
            level={scoreToLevel(data.regional_risk_score || 0)}
            size={140}
          />
        </div>
      </div>

      {/* ===== DISTRIBUTION CARDS ===== */}
      <div className="grid-dashboard" style={{ marginTop: 0 }}>
        {Object.entries(dist).map(([level, count]: [string, any]) => (
          <div key={level} className={`grid-card ${cardColors[level] || ''}`}>
            <div style={{
              fontSize: '0.6rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              opacity: 0.7,
              marginBottom: '0.5rem'
            }}>
              {levelLabels[level] || level}
            </div>
            <div className="t-display t-lg">{count}</div>
          </div>
        ))}
      </div>

      {/* ===== TOP 5 ===== */}
      <div style={{ padding: '1.25rem 6px 0.5rem' }}>
        <span className="t-display" style={{ fontSize: '1.1rem', paddingLeft: '1rem' }}>Watchlist — Top 5</span>
      </div>
      <div className="grid-dashboard" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
        {data.top_5_at_risk?.map((c: any, i: number) => (
          <Link key={c.code} to={`/country/${c.code}`} className="grid-card" style={{ textDecoration: 'none', display: 'block' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <span className="t-label">#{i + 1}</span>
              <div style={{
                width: 8, height: 8,
                background: distColors[c.risk_level] || 'var(--text-muted)',
                borderRadius: '50%'
              }} />
            </div>
            <div className="t-display" style={{ fontSize: '1.1rem', lineHeight: 1.15, marginBottom: '0.5rem' }}>
              {c.name}
            </div>
            <div className="t-data" style={{ fontSize: '1rem', fontWeight: 700, color: distColors[c.risk_level] }}>
              {c.risk_score?.toFixed(1)}
            </div>
          </Link>
        ))}
      </div>

      {/* ===== FULL MATRIX ===== */}
      <div style={{ padding: '1.25rem 6px 0.5rem' }}>
        <span className="t-display" style={{ fontSize: '1.1rem', paddingLeft: '1rem' }}>Matriz Completa</span>
      </div>
      <div className="grid-dashboard">
        {data.countries_by_risk?.map((c: any) => (
          <Link key={c.code} to={`/country/${c.code}`} className="grid-card" style={{ textDecoration: 'none', display: 'block' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.3rem' }}>
              <span style={{ fontFamily: 'var(--font-data)', fontSize: '0.65rem', color: 'var(--text-dim)' }}>{c.code}</span>
              <span style={{
                fontFamily: 'var(--font-data)',
                fontSize: '0.85rem',
                fontWeight: 700,
                color: distColors[c.risk_level]
              }}>
                {c.risk_score?.toFixed(0)}
              </span>
            </div>
            <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{c.name}</div>
          </Link>
        ))}
      </div>
    </div>
  )
}
