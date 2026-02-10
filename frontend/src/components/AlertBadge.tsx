import { AlertLevel } from '../types'

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-low)',
  yellow: 'var(--risk-med)',
  orange: 'var(--risk-med)',
  red: 'var(--risk-high)',
  black: 'var(--risk-black)',
}

const LEVEL_LABELS: Record<AlertLevel, string> = {
  green: 'Stable',
  yellow: 'Watch',
  orange: 'Elevated',
  red: 'Critical',
  black: 'Collapse',
}

interface AlertBadgeProps {
  level: AlertLevel
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  pulsing?: boolean
  className?: string
}

export default function AlertBadge({ level, size = 'md', showLabel = true, pulsing = true, className = '' }: AlertBadgeProps) {
  const color = LEVEL_COLORS[level] || 'var(--text-secondary)'

  const sizeMap = {
    sm: { dot: '6px', font: '0.7rem', padding: '2px 8px' },
    md: { dot: '8px', font: '0.8rem', padding: '4px 10px' },
    lg: { dot: '10px', font: '0.9rem', padding: '6px 14px' },
  }

  const currentSize = sizeMap[size || 'md']

  return (
    <div className={className} style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      background: 'white',
      border: `1px solid ${color}`,
      padding: currentSize.padding,
      borderRadius: '20px', // Pill shape for modern look
      transition: 'all 0.2s ease'
    }}>
      <span style={{
        width: currentSize.dot,
        height: currentSize.dot,
        borderRadius: '50%',
        backgroundColor: color,
        display: 'inline-block',
      }} />

      {showLabel && (
        <span style={{
          color: 'var(--text-primary)',
          fontWeight: 600,
          fontFamily: 'Inter', // Switch to Inter for badge text legality
          fontSize: currentSize.font,
          letterSpacing: '0.02em',
          textTransform: 'uppercase'
        }}>
          {LEVEL_LABELS[level]}
        </span>
      )}
    </div>
  )
}
