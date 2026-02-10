import { useState, useEffect } from 'react'
import { api } from '../services/api'
import CountryCard from '../components/CountryCard'
import AlertPanel from '../components/AlertPanel'
import RiskGauge from '../components/RiskGauge'
import { Country, Alert } from '../types'

export default function Dashboard() {
  const [countries, setCountries] = useState<Country[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Stats
  const [avgRisk, setAvgRisk] = useState(0)
  const [highRiskCount, setHighRiskCount] = useState(0)

  useEffect(() => {
    async function load() {
      try {
        const [countriesData, alertsData] = await Promise.all([
          api.getCountries(),
          api.getAlerts(),
        ])
        setCountries(countriesData)
        setAlerts(alertsData.alerts || [])

        const total = countriesData.reduce((acc: number, c: Country) => acc + c.current_risk_score, 0)
        setAvgRisk(countriesData.length ? total / countriesData.length : 0)
        setHighRiskCount(countriesData.filter((c: Country) => c.current_risk_score >= 70).length)

      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="animate-pulse">Loading Mission Data...</div>
      </div>
    )
  }

  if (error) return <div className="text-red-500 p-4">{error}</div>

  return (
    <div className="animate-enter" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gridAutoRows: 'minmax(180px, auto)', gap: '1.5rem' }}>

      {/* Hero Stats (Top Row) */}
      <div className="bento-card" style={{ gridColumn: 'span 1', background: '#eff6ff', borderColor: '#bfdbfe' }}>
        <div style={{ fontSize: '0.9rem', color: '#1e40af', fontWeight: 600, marginBottom: '0.5rem' }}>ACTIVE ZONES</div>
        <div style={{ fontSize: '3rem', fontWeight: 700, color: '#1e3a8a' }}>{countries.length}</div>
        <div style={{ fontSize: '0.8rem', color: '#60a5fa' }} className="font-mono">MONITORED REGIONS</div>
      </div>

      <div className="bento-card" style={{ gridColumn: 'span 1', background: '#fef2f2', borderColor: '#fecaca' }}>
        <div style={{ fontSize: '0.9rem', color: '#991b1b', fontWeight: 600, marginBottom: '0.5rem' }}>CRITICAL ALERTS</div>
        <div style={{ fontSize: '3rem', fontWeight: 700, color: '#7f1d1d' }}>{highRiskCount}</div>
        <div style={{ fontSize: '0.8rem', color: '#f87171' }} className="font-mono">REQUIRES ATTENTION</div>
      </div>

      <div className="bento-card" style={{ gridColumn: 'span 1' }}>
        <div className="bento-title">AVG RISK SCORE</div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <RiskGauge score={avgRisk} level={avgRisk > 50 ? 'orange' : 'green'} size={120} />
        </div>
      </div>

      <div className="bento-card" style={{ gridColumn: 'span 1', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div className="bento-title">SYSTEM STATUS</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span style={{ width: '10px', height: '10px', background: '#10b981', borderRadius: '50%' }} />
          <span style={{ fontWeight: 600 }}>Operational</span>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Last sync: {new Date().toLocaleTimeString()}</div>
      </div>

      {/* Main Grid (Middle) */}
      <div className="bento-card" style={{ gridColumn: 'span 3', gridRow: 'span 2', overflow: 'hidden' }}>
        <div className="bento-title">
          <span>REGIONAL RISK MATRIX</span>
          <button style={{ fontSize: '0.8rem', color: 'var(--accent)' }}>View Map</button>
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1rem',
          overflowY: 'auto',
          paddingRight: '0.5rem'
        }}>
          {countries.map(country => (
            <CountryCard
              key={country.code}
              code={country.code}
              name={country.name}
              region={country.region}
              riskScore={country.current_risk_score}
              riskLevel={country.current_risk_level}
            />
          ))}
        </div>
      </div>

      {/* Sidebar / Alerts (Right) */}
      <div className="bento-card" style={{ gridColumn: 'span 1', gridRow: 'span 2', padding: 0, overflow: 'hidden' }}>
        <AlertPanel alerts={alerts} />
      </div>

    </div>
  )
}
