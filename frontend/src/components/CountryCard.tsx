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
  green: 'var(--green)',
  yellow: 'var(--yellow)',
  orange: 'var(--orange)',
  red: 'var(--red)',
  black: 'var(--black-alert)',
}

export default function CountryCard({ code, name, region, riskScore, riskLevel, domainScores }: CountryCardProps) {
  const color = LEVEL_COLORS[riskLevel] || 'var(--text-muted)'

  return (
    <Link to={`/country/${code}`} style={{ textDecoration: 'none', display: 'block' }}>
      <div className="glass-card" style={{
        padding: '1.25rem',
        borderRadius: '8px',
        position: 'relative',
        overflow: 'hidden',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        {/* Left Border Indicator */}
        <div style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: '4px',
          background: `linear-gradient(to bottom, ${color}, transparent)`
        }} />

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
          <div>
            <div style={{
              fontFamily: 'JetBrains Mono',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              marginBottom: '0.25rem'
            }}>
              {code}
            </div>
            <h3 style={{
              color: 'var(--text-primary)',
              margin: 0,
              fontSize: '1.1rem',
              fontWeight: 600,
              letterSpacing: '-0.01em'
            }}>
              {name}
            </h3>
          </div>
          <AlertBadge level={riskLevel} size="sm" showLabel={false} pulsing={false} />
        </div>

        {/* Risk Score */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '1rem' }}>
          <span style={{
            color: 'var(--text-primary)',
            fontWeight: 700,
            fontSize: '2rem',
            fontFamily: 'JetBrains Mono',
            lineHeight: 1,
            textShadow: `0 0 15px ${color}40`
          }}>
            {riskScore.toFixed(0)}
          </span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontFamily: 'JetBrains Mono' }}>/100</span>
        </div>

        {/* Mini Sparklines */}
        {domainScores && Object.keys(domainScores).length > 0 && (
          <div style={{ display: 'flex', gap: '4px', marginTop: 'auto' }}>
            {Object.entries(domainScores).map(([domain, score]) => (
              <div key={domain} style={{
                flex: 1,
                height: '3px',
                borderRadius: '1.5px',
                backgroundColor: score > 70 ? 'var(--red)' : score > 50 ? 'var(--orange)' : score > 30 ? 'var(--yellow)' : 'rgba(255,255,255,0.1)',
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
