import { AlertLevel } from '../types'

interface RiskGaugeProps {
  score: number
  level: AlertLevel
  label?: string
}

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--green)',
  yellow: 'var(--yellow)',
  orange: 'var(--orange)',
  red: 'var(--red)',
  black: 'var(--black-alert)',
}

export default function RiskGauge({ score, level, label }: RiskGaugeProps) {
  const color = LEVEL_COLORS[level] || 'var(--text-muted)'
  const percentage = Math.min(100, Math.max(0, score))

  return (
    <div style={{ textAlign: 'center' }}>
      {label && (
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
          {label}
        </div>
      )}
      <div style={{
        position: 'relative',
        width: '120px',
        height: '120px',
        margin: '0 auto',
      }}>
        <svg viewBox="0 0 120 120" width="120" height="120">
          {/* Background circle */}
          <circle
            cx="60" cy="60" r="50"
            fill="none"
            stroke="var(--border)"
            strokeWidth="10"
            strokeDasharray="235.6"
            strokeDashoffset="0"
            transform="rotate(-90 60 60)"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <circle
            cx="60" cy="60" r="50"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeDasharray="235.6"
            strokeDashoffset={235.6 * (1 - percentage / 100)}
            transform="rotate(-90 60 60)"
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '1.8rem', fontWeight: 'bold', fontFamily: 'monospace', color }}>
            {score.toFixed(0)}
          </div>
        </div>
      </div>
    </div>
  )
}
