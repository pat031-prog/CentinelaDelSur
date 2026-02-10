import { useState, useEffect } from 'react'
import { api } from '../services/api'
import CountryCard from '../components/CountryCard'
import AlertPanel from '../components/AlertPanel'
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

        // Calculate stats
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
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '60vh',
        color: 'var(--text-muted)'
      }}>
        <div style={{
          width: '200px',
          height: '2px',
          background: 'rgba(56, 189, 248, 0.1)',
          position: 'relative',
          overflow: 'hidden',
          marginBottom: '1rem'
        }}>
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            height: '100%',
            width: '50%',
            background: 'var(--accent)',
            animation: 'scan-line 1.5s infinite linear'
          }} />
        </div>
        <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.85rem', letterSpacing: '0.1em' }}>
          INITIALIZING ATALAYA...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        textAlign: 'center',
        padding: '4rem',
        color: 'var(--red)',
        background: 'var(--bg-card)',
        borderRadius: '8px',
        border: '1px solid var(--border)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem', fontFamily: 'JetBrains Mono' }}>CONNECTION LOST</div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{error}</div>
      </div>
    )
  }

  return (
    <div className="animate-fade-in-up">
      {/* Hero Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <StatCard label="MONITORED REGIONS" value={countries.length.toString()} icon="🌐" />
        <StatCard label="ACTIVE THREATS" value={alerts.length.toString()} icon="⚠️" color="var(--orange)" />
        <StatCard label="AVG REGIONAL RISK" value={avgRisk.toFixed(1)} icon="📊" suffix="/100" />
        <StatCard label="CRITICAL ZONES" value={highRiskCount.toString()} icon="🚨" color="var(--red)" pulsing />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 380px', gap: '2rem' }}>
        {/* Main Grid */}
        <div>
          <h2 style={{
            fontSize: '0.9rem',
            marginBottom: '1rem',
            color: 'var(--text-secondary)',
            letterSpacing: '0.1em',
            fontFamily: 'JetBrains Mono'
          }}>
            SYSTEMIC RISK MATRIX
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '1.25rem'
          }}>
            {countries.map((country, index) => (
              <div key={country.code} style={{ animationDelay: `${index * 50}ms` }} className="animate-fade-in-up">
                <CountryCard
                  code={country.code}
                  name={country.name}
                  region={country.region}
                  riskScore={country.current_risk_score}
                  riskLevel={country.current_risk_level}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div style={{ position: 'sticky', top: 'calc(var(--nav-height) + 2rem)', height: 'calc(100vh - var(--nav-height) - 4rem)' }}>
          <AlertPanel alerts={alerts} />
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon, color = 'var(--accent)', suffix, pulsing }: any) {
  return (
    <div className="glass-panel" style={{
      padding: '1.25rem',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem'
    }}>
      <div style={{
        fontSize: '1.5rem',
        width: '48px',
        height: '48px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(255,255,255,0.03)',
        borderRadius: '8px',
        border: '1px solid var(--border)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {pulsing && <div style={{
          position: 'absolute', inset: 0, background: color, opacity: 0.2, animation: 'pulse-glow 2s infinite'
        }} />}
        {icon}
      </div>
      <div>
        <div style={{
          fontSize: '0.7rem',
          color: 'var(--text-secondary)',
          fontFamily: 'JetBrains Mono',
          letterSpacing: '0.05em'
        }}>
          {label}
        </div>
        <div style={{
          fontSize: '1.5rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          fontFamily: 'JetBrains Mono',
          lineHeight: 1,
          marginTop: '0.2rem',
          textShadow: `0 0 10px ${color}40`
        }}>
          {value}
          {suffix && <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginLeft: '4px' }}>{suffix}</span>}
        </div>
      </div>
    </div>
  )
}
