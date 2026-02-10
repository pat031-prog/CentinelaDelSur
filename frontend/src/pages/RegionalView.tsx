import { useState, useEffect } from 'react'
import { api } from '../services/api'
import CountryCard from '../components/CountryCard'
import RiskGauge from '../components/RiskGauge'

export default function RegionalView() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const result = await api.getRegionalOverview()
        setData(result)
      } catch (e) {
        console.error('Failed to load regional data:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
      Scanning Latin American region...
    </div>
  }

  if (!data) {
    return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--red)' }}>Failed to load data</div>
  }

  const scoreToLevel = (score: number) => {
    if (score >= 85) return 'black' as const
    if (score >= 70) return 'red' as const
    if (score >= 50) return 'orange' as const
    if (score >= 30) return 'yellow' as const
    return 'green' as const
  }

  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Regional Overview - Latin America</h1>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '2rem' }}>
        {data.total_countries} countries monitored
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '1.5rem',
          textAlign: 'center',
        }}>
          <RiskGauge
            score={data.regional_risk_score}
            level={scoreToLevel(data.regional_risk_score)}
            label="Regional Risk Score"
          />
        </div>

        {data.risk_distribution && Object.entries(data.risk_distribution).map(([level, count]) => (
          <div key={level} style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '1.25rem',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', fontFamily: 'monospace' }}>{count as number}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase' }}>{level}</div>
          </div>
        ))}
      </div>

      <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
        All Countries by Risk
      </h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '1rem'
      }}>
        {data.countries_by_risk?.map((country: any) => (
          <CountryCard
            key={country.code}
            code={country.code}
            name={country.name}
            region={country.region}
            riskScore={country.risk_score}
            riskLevel={country.risk_level}
            domainScores={country.domain_scores}
          />
        ))}
      </div>
    </div>
  )
}
