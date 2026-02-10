import { Link } from 'react-router-dom'
import AlertBadge from './AlertBadge'
import { AlertLevel } from '../types'

interface CountryCardProps {
  code: string
  name: string
  region: string
  riskScore: number
  riskLevel: AlertLevel
  domainScores?: Record<string, number>
}

export default function CountryCard({ code, name, region, riskScore, riskLevel, domainScores }: CountryCardProps) {
  return (
    <Link to={`/country/${code}`} style={{ textDecoration: 'none' }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        padding: '1.25rem',
        transition: 'border-color 0.2s, transform 0.2s',
        cursor: 'pointer',
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--accent)'
        ;(e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)'
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border)'
        ;(e.currentTarget as HTMLDivElement).style.transform = 'none'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
          <div>
            <h3 style={{ color: 'var(--text-primary)', margin: 0, fontSize: '1.1rem' }}>{name}</h3>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{code} | {region}</span>
          </div>
          <AlertBadge level={riskLevel} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Risk Score:</span>
          <span style={{
            color: 'var(--text-primary)',
            fontWeight: 'bold',
            fontSize: '1.5rem',
            fontFamily: 'monospace',
          }}>
            {riskScore.toFixed(1)}
          </span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>/100</span>
        </div>

        {domainScores && Object.keys(domainScores).length > 0 && (
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {Object.entries(domainScores).map(([domain, score]) => (
              <div key={domain} style={{
                flex: 1,
                minWidth: '40px',
                height: '4px',
                borderRadius: '2px',
                backgroundColor: score > 70 ? 'var(--red)' : score > 50 ? 'var(--orange)' : score > 30 ? 'var(--yellow)' : 'var(--green)',
                opacity: 0.8,
              }}
              title={`${domain}: ${score}`}
              />
            ))}
          </div>
        )}
      </div>
    </Link>
  )
}
