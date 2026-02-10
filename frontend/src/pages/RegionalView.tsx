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

  if (loading) return <div className="p-8 text-center text-slate-500">Scanning Region...</div>
  if (!data) return <div className="p-8 text-center text-red-600">Region Data Unavailable</div>

  const scoreToLevel = (score: number) => {
    if (score >= 85) return 'black' as const
    if (score >= 70) return 'red' as const
    if (score >= 50) return 'orange' as const
    if (score >= 30) return 'yellow' as const
    return 'green' as const
  }

  return (
    <div className="animate-enter">
      <div style={{ marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          Regional Intelligence
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Real-time monitoring of {data.total_countries} sovereign entities
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem', marginBottom: '3rem' }}>
        <div className="bento-card" style={{ padding: '2rem', textAlign: 'center', justifyContent: 'center' }}>
          <div className="bento-title" style={{ justifyContent: 'center' }}>THREAT INDEX</div>
          <RiskGauge
            score={data.regional_risk_score}
            level={scoreToLevel(data.regional_risk_score)}
            size={160}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
          {data.risk_distribution && Object.entries(data.risk_distribution).map(([level, count]: [string, any]) => {
            const colors: any = { green: '#10b981', yellow: '#f59e0b', orange: '#f97316', red: '#dc2626', black: '#7c3aed' }
            const color = colors[level]

            return (
              <div key={level} className="bento-card" style={{
                textAlign: 'center',
                justifyContent: 'center',
                borderTop: `4px solid ${color}`
              }}>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1, marginBottom: '0.5rem' }}>
                  {count}
                </div>
                <div style={{ color: color, fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
                  {level}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="bento-title">FULL REGIONAL MATRIX</div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '1.25rem'
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
