import { AlertLevel } from '../types'

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--green)',
  yellow: 'var(--yellow)',
  orange: 'var(--orange)',
  red: 'var(--red)',
  black: 'var(--black-alert)',
}

const LEVEL_LABELS: Record<AlertLevel, string> = {
  green: 'ALL CLEAR',
  yellow: 'WATCHLIST',
  orange: 'ELEVATED',
  red: 'CRITICAL',
  black: 'COLLAPSE',
}

interface AlertBadgeProps {
  level: AlertLevel
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  pulsing?: boolean
  className?: string
}

export default function AlertBadge({ level, size = 'md', showLabel = true, pulsing = true, className = '' }: AlertBadgeProps) {
  const color = LEVEL_COLORS[level] || 'var(--text-muted)'

  const sizeMap = {
    sm: { dot: '6px', font: '0.7rem', padding: '2px 6px' },
    md: { dot: '8px', font: '0.8rem', padding: '4px 8px' },
    lg: { dot: '10px', font: '0.9rem', padding: '6px 12px' },
  }

  const currentSize = sizeMap[size || 'md']

  // Only pulse for severe threats
  const shouldPulse = pulsing && (level === 'red' || level === 'black')
  const animationName = level === 'black' ? 'pulse-glow-black' : 'pulse-glow'

  return (
    <div className={className} style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      background: `rgba(0,0,0,0.2)`,
      border: `1px solid ${color}`,
      padding: currentSize.padding,
      borderRadius: '4px',
      boxShadow: shouldPulse ? `0 0 8px ${color}20` : 'none',
      transition: 'all 0.3s ease'
    }}>
      <span style={{
        width: currentSize.dot,
        height: currentSize.dot,
        borderRadius: '50%',
        backgroundColor: color,
        display: 'inline-block',
        boxShadow: `0 0 6px ${color}80`,
        animation: shouldPulse ? `${animationName} 2s infinite` : 'none',
      }} />

      {showLabel && (
        <span style={{
          color: color,
          fontWeight: 600,
          fontFamily: 'JetBrains Mono',
          fontSize: currentSize.font,
          letterSpacing: '0.05em',
          textShadow: `0 0 8px ${color}40`,
          textTransform: 'uppercase'
        }}>
          {LEVEL_LABELS[level]}
        </span>
      )}
    </div>
  )
}
