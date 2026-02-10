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
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh'
      }}>
        <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.85rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>
          SCANNING LATAM REGION...
        </div>
        <div style={{ width: '100px', height: '1px', background: 'var(--accent)', marginTop: '1rem', animation: 'scan-line 1s infinite' }} />
      </div>
    )
  }

  if (!data) return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--red)' }}>DATA STREAM INTERRUPTED</div>

  const scoreToLevel = (score: number) => {
    if (score >= 85) return 'black' as const
    if (score >= 70) return 'red' as const
    if (score >= 50) return 'orange' as const
    if (score >= 30) return 'yellow' as const
    return 'green' as const
  }

  return (
    <div className="animate-fade-in-up">
      {/* Header */}
      <div style={{ marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', letterSpacing: '-0.02em', textShadow: '0 0 15px rgba(56, 189, 248, 0.3)' }}>
          REGIONAL SITUATIONAL AWARENESS
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontFamily: 'JetBrains Mono' }}>
          Monitoring {data.total_countries} sovereign entities across Latin America
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem', marginBottom: '3rem' }}>
        {/* Risk Score Panel */}
        <div className="glass-panel" style={{
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          background: 'linear-gradient(145deg, rgba(16, 24, 39, 0.8) 0%, rgba(16, 24, 39, 0.4) 100%)'
        }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem', fontFamily: 'JetBrains Mono', letterSpacing: '0.1em' }}>
            REGIONAL THREAT INDEX
          </h3>
          <RiskGauge
            score={data.regional_risk_score}
            level={scoreToLevel(data.regional_risk_score)}
            size={160}
          />
        </div>

        {/* Risk Distribution Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
          {data.risk_distribution && Object.entries(data.risk_distribution).map(([level, count]: [string, any]) => {
            const colors: any = { green: 'var(--green)', yellow: 'var(--yellow)', orange: 'var(--orange)', red: 'var(--red)', black: 'var(--black-alert)' }
            const color = colors[level] || 'var(--text-muted)'

            return (
              <div key={level} className="glass-card" style={{
                padding: '1.5rem',
                borderRadius: '8px',
                textAlign: 'center',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                borderTop: `2px solid ${color}`
              }}>
                <div style={{
                  fontSize: '2.5rem',
                  fontWeight: 700,
                  fontFamily: 'JetBrains Mono',
                  color: 'var(--text-primary)',
                  lineHeight: 1,
                  marginBottom: '0.5rem',
                  textShadow: `0 0 10px ${color}40`
                }}>
                  {count}
                </div>
                <div style={{
                  color: color,
                  fontSize: '0.75rem',
                  fontFamily: 'JetBrains Mono',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  {level}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <h2 style={{
        fontSize: '1.1rem',
        marginBottom: '1.5rem',
        color: 'var(--text-secondary)',
        fontFamily: 'JetBrains Mono',
        letterSpacing: '0.1em',
        paddingLeft: '1rem',
        borderLeft: '2px solid var(--accent)'
      }}>
        FULL REGIONAL MATRIX
      </h2>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '1.25rem'
      }}>
        {data.countries_by_risk?.map((country: any, index: number) => (
          <div key={country.code} className="animate-fade-in-up" style={{ animationDelay: `${index * 50}ms` }}>
            <CountryCard
              code={country.code}
              name={country.name}
              region={country.region}
              riskScore={country.risk_score}
              riskLevel={country.risk_level}
              domainScores={country.domain_scores}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
