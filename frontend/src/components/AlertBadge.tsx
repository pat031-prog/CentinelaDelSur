import { AlertLevel } from '../types'

const COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-green)',
  yellow: 'var(--risk-yellow)',
  orange: 'var(--risk-orange)',
  red: 'var(--risk-red)',
  black: 'var(--risk-black)',
}

const LABELS: Record<AlertLevel, string> = {
  green: 'Estable',
  yellow: 'Vigilancia',
  orange: 'Elevado',
  red: 'Crítico',
  black: 'Colapso',
}

interface Props {
  level: AlertLevel
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  pulsing?: boolean
  className?: string
}

export default function AlertBadge({ level, size = 'md', showLabel = true }: Props) {
  const color = COLORS[level] || 'var(--text-muted)'

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: size === 'sm' ? '2px 8px' : '4px 12px',
      border: `1px solid ${color}`,
      background: 'transparent',
      color: color,
      fontFamily: 'var(--font-mono)',
      fontSize: size === 'sm' ? '0.65rem' : '0.75rem',
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
      borderRadius: 0 // Explicit square
    }}>
      <div style={{
        width: size === 'sm' ? 6 : 8,
        height: size === 'sm' ? 6 : 8,
        background: color,
        borderRadius: 0 // Square dot
      }} />
      {showLabel && (
        <span>{LABELS[level]}</span>
      )}
    </div>
  )
}
