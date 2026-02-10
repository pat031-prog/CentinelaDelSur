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

  useEffect(() => {
    async function load() {
      try {
        const [countriesData, alertsData] = await Promise.all([
          api.getCountries(),
          api.getAlerts(),
        ])
        setCountries(countriesData)
        setAlerts(alertsData.alerts || [])
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
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
        <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Scanning multiple data sources...</div>
        <div style={{ fontSize: '0.85rem' }}>Initializing ATALAYA threat assessment</div>
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
      }}>
        <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Connection Error</div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{error}</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '1rem' }}>
          Ensure the backend is running at http://localhost:8000
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
          Systemic Risk Dashboard - Latin America
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Real-time monitoring of {countries.length} countries across 6 risk domains
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
            Countries by Risk Level
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '1rem'
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

        <div>
          <AlertPanel alerts={alerts} />
        </div>
      </div>
    </div>
  )
}
