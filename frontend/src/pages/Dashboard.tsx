import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import AlertBadge from '../components/AlertBadge'
import { Country, Alert } from '../types'

export default function Dashboard() {
  const [countries, setCountries] = useState<Country[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [c, a] = await Promise.all([api.getCountries(), api.getAlerts()])
        setCountries(c)
        setAlerts(a.alerts || [])
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Error de conexión')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSkeleton />
  if (error) return <ErrorState message={error} />

  const critical = countries.filter(c => c.current_risk_score >= 70)
  const watchlist = countries.filter(c => c.current_risk_score >= 40 && c.current_risk_score < 70)
  const stable = countries.filter(c => c.current_risk_score < 40)
  const avgRisk = countries.length
    ? countries.reduce((a, c) => a + c.current_risk_score, 0) / countries.length
    : 0

  return (
    <div className="fade-in">
      {/* ===== SALUDO + RESUMEN ===== */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>Sala de Situación</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '640px', lineHeight: 1.6 }}>
          ATALAYA monitorea <strong>{countries.length} entidades soberanas</strong> en América Latina.{' '}
          {critical.length > 0
            ? <>Actualmente <strong style={{ color: 'var(--risk-red)' }}>{critical.length} zona{critical.length > 1 ? 's' : ''}</strong> requiere{critical.length > 1 ? 'n' : ''} atención inmediata.</>
            : <>Todos los indicadores dentro de parámetros aceptables.</>
          }
        </p>
      </div>

      {/* ===== TARJETAS ESTADÍSTICAS ===== */}
      <div className="stats-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem',
      }}>
        <StatCard label="Monitoreados" value={`${countries.length}`} sub="Regiones activas" bg="card--cream" />
        <StatCard
          label="Críticos"
          value={`${critical.length}`}
          sub={critical.length > 0 ? critical.map(c => c.code).join(', ') : 'Ninguno'}
          bg="card--salmon"
        />
        <StatCard label="Vigilancia" value={`${watchlist.length}`} sub="Monitoreo elevado" bg="card--sage" />
        <StatCard label="Riesgo Prom." value={avgRisk.toFixed(1)} sub="Compuesto regional" bg="card--lavender" />
      </div>

      {/* ===== LAYOUT 2 COLUMNAS ===== */}
      <div className="dashboard-layout" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 360px',
        gap: '1.5rem',
        alignItems: 'start',
      }}>
        {/* IZQUIERDA: Matriz de Países */}
        <div className="country-matrix">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3>Matriz de Países</h3>
            <Link to="/regional" style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
              Ver todos →
            </Link>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '1rem',
          }}>
            {countries.map((country, i) => (
              <CountryRow key={country.code} country={country} index={i} />
            ))}
          </div>
        </div>

        {/* DERECHA: Feed de Inteligencia */}
        <div className="card intelligence-feed" style={{ padding: 0, overflow: 'hidden', position: 'sticky', top: '5.5rem' }}>
          <div style={{
            padding: '1rem 1.25rem',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--risk-red)', display: 'inline-block', animation: 'pulse 2s infinite' }} />
              <span className="label">FEED DE INTELIGENCIA EN VIVO</span>
            </div>
            <span className="pill" style={{ fontSize: '0.7rem' }}>{alerts.length}</span>
          </div>

          <div style={{ maxHeight: '520px', overflowY: 'auto' }}>
            {alerts.length === 0 ? (
              <div style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                No se detectaron señales activas.
              </div>
            ) : (
              alerts.slice(0, 8).map(alert => (
                <AlertRow key={alert.id} alert={alert} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/* ===== SUB-COMPONENTES ===== */

function StatCard({ label, value, sub, bg }: { label: string; value: string; sub: string; bg: string }) {
  return (
    <div className={`card ${bg}`} style={{ padding: '1.25rem' }}>
      <div className="label" style={{ marginBottom: '0.75rem', color: 'rgba(0,0,0,0.45)' }}>{label}</div>
      <div className="stat-number" style={{ color: 'var(--text-primary)' }}>{value}</div>
      <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'rgba(0,0,0,0.5)', fontWeight: 500 }}>{sub}</div>
    </div>
  )
}

function CountryRow({ country, index }: { country: Country; index: number }) {
  const riskColor = getRiskColor(country.current_risk_score)

  return (
    <Link
      to={`/country/${country.code}`}
      style={{ textDecoration: 'none', animationDelay: `${index * 40}ms` }}
      className="fade-in"
    >
      <div className="card" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 1.25rem',
        borderLeft: `3px solid ${riskColor}`,
        cursor: 'pointer',
      }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '2px' }}>{country.name}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>{country.code}</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>·</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{country.region}</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 60, height: 6, borderRadius: 3, background: '#e8e3da', overflow: 'hidden' }}>
            <div style={{ width: `${country.current_risk_score}%`, height: '100%', background: riskColor, borderRadius: 3 }} />
          </div>
          <span style={{ fontWeight: 800, fontSize: '1.1rem', minWidth: 30, textAlign: 'right', color: riskColor }}>
            {country.current_risk_score.toFixed(0)}
          </span>
          <AlertBadge level={country.current_risk_level} size="sm" showLabel={false} />
        </div>
      </div>
    </Link>
  )
}

function AlertRow({ alert }: { alert: Alert }) {
  const handleClick = () => {
    if (alert.source_url) {
      window.open(alert.source_url, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <div style={{
      padding: '0.875rem 1.25rem',
      borderBottom: '1px solid rgba(0,0,0,0.04)',
      cursor: alert.source_url ? 'pointer' : 'default',
      transition: 'background 0.15s, transform 0.1s',
    }}
      onClick={handleClick}
      onMouseEnter={e => {
        e.currentTarget.style.background = 'rgba(0,0,0,0.03)'
        e.currentTarget.style.transform = 'translateX(2px)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = 'transparent'
        e.currentTarget.style.transform = 'translateX(0)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
        <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)' }}>{alert.country_code}</span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {new Date(alert.created_at).toLocaleDateString('es-419', { month: 'short', day: 'numeric' })}
        </span>
      </div>
      <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '4px', lineHeight: 1.3 }}>{alert.title}</div>
      <div style={{
        fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4,
        display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as const, overflow: 'hidden',
      }}>{alert.description}</div>

      {/* Editorial micro-analysis */}
      {alert.editorial && (
        <div style={{
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          fontStyle: 'italic',
          lineHeight: 1.4,
          marginTop: '6px',
          padding: '6px 8px',
          background: 'rgba(0,0,0,0.02)',
          borderRadius: 4,
          borderLeft: '2px solid var(--border)',
        }}>
          {alert.editorial}
        </div>
      )}

      <div style={{ marginTop: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <AlertBadge level={alert.alert_level} size="sm" />
        {alert.source_url && (
          <span style={{
            fontSize: '0.7rem',
            color: 'var(--accent)',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '3px',
          }}>
            Ver fuente ↗
          </span>
        )}
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ height: 28, width: 200, background: 'var(--border)', borderRadius: 6, marginBottom: '1rem' }} />
      <div style={{ height: 16, width: 400, background: 'var(--border)', borderRadius: 6, marginBottom: '2rem' }} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        {[1, 2, 3, 4].map(i => (
          <div key={i} style={{ height: 120, background: 'var(--border)', borderRadius: 'var(--radius)', opacity: 0.5 }} />
        ))}
      </div>
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="card card--salmon" style={{ padding: '2rem', textAlign: 'center', maxWidth: 480, margin: '4rem auto' }}>
      <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠</div>
      <h3 style={{ marginBottom: '0.5rem' }}>Error de Conexión</h3>
      <p style={{ color: 'rgba(0,0,0,0.6)', fontSize: '0.9rem' }}>{message}</p>
      <button className="btn btn--primary" onClick={() => window.location.reload()} style={{ marginTop: '1rem' }}>
        Reintentar
      </button>
    </div>
  )
}

function getRiskColor(score: number): string {
  if (score >= 85) return 'var(--risk-black)'
  if (score >= 70) return 'var(--risk-red)'
  if (score >= 50) return 'var(--risk-orange)'
  if (score >= 30) return 'var(--risk-yellow)'
  return 'var(--risk-green)'
}
