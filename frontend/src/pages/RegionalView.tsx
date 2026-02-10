import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import AlertBadge from '../components/AlertBadge'
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

  if (loading) return <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Escaneando región...</div>
  if (!data) return <div style={{ padding: '3rem', color: 'var(--risk-red)' }}>Región no disponible</div>

  const scoreToLevel = (s: number) => {
    if (s >= 85) return 'black' as const
    if (s >= 70) return 'red' as const
    if (s >= 50) return 'orange' as const
    if (s >= 30) return 'yellow' as const
    return 'green' as const
  }

  const dist = data.risk_distribution || {}
  const distColors: Record<string, string> = {
    green: 'var(--risk-green)', yellow: 'var(--risk-yellow)',
    orange: 'var(--risk-orange)', red: 'var(--risk-red)', black: 'var(--risk-black)',
  }

  const levelLabels: Record<string, string> = {
    green: 'Estable', yellow: 'Vigilancia', orange: 'Elevado', red: 'Crítico', black: 'Colapso',
  }

  return (
    <div className="fade-in">
      {/* Encabezado */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>Inteligencia Regional</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '600px', lineHeight: 1.6 }}>
          Escaneo hemisférico de <strong>{data.total_countries}</strong> entidades soberanas.
          El índice de fragilidad regional promedio se sitúa en <strong style={{
            color: data.regional_risk_score >= 50 ? 'var(--risk-orange)' : 'var(--text-primary)'
          }}>{data.regional_risk_score?.toFixed(1)}</strong>.
        </p>
      </div>

      {/* ===== GAUGE + DISTRIBUCIÓN ===== */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '280px 1fr',
        gap: '1.5rem',
        marginBottom: '2.5rem',
      }}>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div className="label" style={{ marginBottom: '1rem' }}>ÍNDICE DE AMENAZA HEMISFÉRICA</div>
          <RiskGauge
            score={data.regional_risk_score || 0}
            level={scoreToLevel(data.regional_risk_score || 0)}
            size={150}
          />
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
          gap: '1rem',
        }}>
          {Object.entries(dist).map(([level, count]: [string, any]) => {
            const colorMap: Record<string, string> = {
              green: 'card--sage', yellow: 'card--cream', orange: 'card--salmon',
              red: 'card--blush', black: 'card--lavender',
            }
            return (
              <div key={level} className={`card ${colorMap[level] || ''}`} style={{
                padding: '1.25rem',
                textAlign: 'center',
                display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
              }}>
                <div className="stat-number" style={{ fontSize: '2rem' }}>{count}</div>
                <div style={{
                  fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
                  letterSpacing: '0.08em', color: distColors[level] || 'var(--text-muted)',
                  marginTop: '0.375rem',
                }}>{levelLabels[level] || level}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ===== TOP 5 ===== */}
      {data.top_5_at_risk?.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div className="label" style={{ marginBottom: '1rem' }}>TOP 5 — MAYOR RIESGO</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {data.top_5_at_risk.map((c: any, i: number) => (
              <Link key={c.code} to={`/country/${c.code}`} style={{ textDecoration: 'none' }}>
                <div className="card card--salmon" style={{
                  padding: '1.25rem',
                  borderLeft: `4px solid ${distColors[c.risk_level] || 'var(--border)'}`,
                  cursor: 'pointer',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{c.name}</span>
                    <span className="pill" style={{ fontSize: '0.65rem' }}>#{i + 1}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                    <span className="stat-number" style={{ fontSize: '1.75rem' }}>{c.risk_score?.toFixed(0)}</span>
                    <AlertBadge level={c.risk_level} size="sm" showLabel={false} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* ===== TODAS LAS ENTIDADES ===== */}
      <div className="label" style={{ marginBottom: '1rem' }}>TODAS LAS ENTIDADES</div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '1rem',
      }}>
        {data.countries_by_risk?.map((c: any) => (
          <Link key={c.code} to={`/country/${c.code}`} style={{ textDecoration: 'none' }}>
            <div className="card" style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderLeft: `3px solid ${distColors[c.risk_level] || 'var(--border)'}`,
              cursor: 'pointer',
            }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '2px' }}>{c.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{c.code} · {c.region}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: 50, height: 5, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
                  <div style={{ width: `${c.risk_score}%`, height: '100%', background: distColors[c.risk_level], borderRadius: 3 }} />
                </div>
                <span style={{ fontWeight: 800, fontSize: '1rem', color: distColors[c.risk_level], minWidth: 28, textAlign: 'right' }}>
                  {c.risk_score?.toFixed(0)}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
