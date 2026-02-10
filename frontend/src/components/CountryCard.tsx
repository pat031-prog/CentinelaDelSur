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

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-low)',
  yellow: 'var(--risk-med)',
  orange: 'var(--risk-med)', // Using amber for both yellow/orange in light mode for better contrast
  red: 'var(--risk-high)',
  black: 'var(--risk-black)',
}

export default function CountryCard({ code, name, region, riskScore, riskLevel, domainScores }: CountryCardProps) {
  const color = LEVEL_COLORS[riskLevel] || 'var(--text-secondary)'

  return (
    <Link to={`/country/${code}`} style={{ textDecoration: 'none', display: 'block', height: '100%' }}>
      <div className="bento-card" style={{
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        borderLeft: `4px solid ${color}`,
        padding: '1.25rem',
        justifyContent: 'space-between'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
          <div>
            <div style={{
              fontFamily: 'JetBrains Mono',
              fontSize: '0.75rem',
              color: 'var(--text-secondary)',
              marginBottom: '0.25rem',
              fontWeight: 600
            }}>
              {code}
            </div>
            <h3 style={{
              color: 'var(--text-primary)',
              margin: 0,
              fontSize: '1.1rem',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              lineHeight: 1.2
            }}>
              {name}
            </h3>
          </div>
          <AlertBadge level={riskLevel} size="sm" showLabel={false} pulsing={false} />
        </div>

        {/* Risk Score */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginTop: 'auto' }}>
          <span style={{
            color: 'var(--text-primary)',
            fontWeight: 800,
            fontSize: '2rem',
            fontFamily: 'JetBrains Mono',
            lineHeight: 1
          }}>
            {riskScore.toFixed(0)}
          </span>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontFamily: 'JetBrains Mono' }}>/100</span>
        </div>

        {/* Sparkline Decor (Simplified) */}
        <div style={{
          height: '4px',
          width: '100%',
          background: '#f1f5f9',
          marginTop: '0.75rem',
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${riskScore}%`,
            height: '100%',
            background: color,
            transition: 'width 1s ease-out'
          }} />
        </div>
      </div>
    </Link>
  )
}
