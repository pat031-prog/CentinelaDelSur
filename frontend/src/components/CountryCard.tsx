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
      <div className="card" style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        borderLeft: `6px solid ${color}`, // Thicker archival marker
        padding: '1.25rem'
      }}>
        {/* Header Ficha */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <span className="label-archive" style={{ background: 'black', color: 'white', padding: '2px 6px', display: 'inline-block' }}>
              {code}
            </span>
            <h3 style={{
              marginTop: '0.75rem',
              fontSize: '1.25rem',
              lineHeight: 1.1,
              marginBottom: '0.25rem'
            }}>
              {name}
            </h3>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              {region}
            </span>
          </div>

          {/* Score Serif Giant */}
          <div style={{ textAlign: 'right' }}>
            <span style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '2.5rem',
              fontWeight: 700,
              lineHeight: 1,
              color: 'var(--text-primary)'
            }}>
              {riskScore.toFixed(0)}
            </span>
            <div style={{ fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: '4px' }}>
              INDICE
            </div>
          </div>
        </div>

        {/* Footer / Status */}
        <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border-light)', paddingTop: '0.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>ESTADO:</span>
            <AlertBadge level={riskLevel} size="sm" />
          </div>
        </div>
      </div>
    </Link>
  )
}
