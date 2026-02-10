import { AlertLevel } from '../types'

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--green)',
  yellow: 'var(--yellow)',
  orange: 'var(--orange)',
  red: 'var(--red)',
  black: 'var(--black-alert)',
}

const LEVEL_LABELS: Record<AlertLevel, string> = {
  green: 'LOW',
  yellow: 'MODERATE',
  orange: 'ELEVATED',
  red: 'HIGH',
  black: 'CRITICAL',
}

interface AlertBadgeProps {
  level: AlertLevel
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export default function AlertBadge({ level, size = 'md', showLabel = true }: AlertBadgeProps) {
  const color = LEVEL_COLORS[level] || 'var(--text-muted)'
  const sizes = { sm: '0.75rem', md: '1rem', lg: '1.5rem' }

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
    }}>
      <span style={{
        width: sizes[size],
        height: sizes[size],
        borderRadius: '50%',
        backgroundColor: color,
        display: 'inline-block',
        boxShadow: `0 0 8px ${color}40`,
      }} />
      {showLabel && (
        <span style={{
          color,
          fontWeight: 600,
          fontSize: size === 'sm' ? '0.7rem' : size === 'lg' ? '1rem' : '0.85rem',
          letterSpacing: '0.05em',
        }}>
          {LEVEL_LABELS[level] || level.toUpperCase()}
        </span>
      )}
    </span>
  )
}
