import { AlertLevel } from '../types'

const COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-low)',
  yellow: 'var(--risk-medium)',
  orange: 'var(--risk-high)',
  red: 'var(--risk-critical)',
  black: 'var(--text-primary)',
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
      gap: '0.35rem',
      padding: size === 'sm' ? '2px 6px' : '3px 10px',
      border: `1px solid ${color}`,
      borderRadius: 'var(--radius-xs)',
      background: 'transparent',
      color: color,
      fontFamily: 'var(--font-data)',
      fontSize: size === 'sm' ? '0.6rem' : '0.65rem',
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: '0.03em',
    }}>
      <div style={{
        width: size === 'sm' ? 5 : 6,
        height: size === 'sm' ? 5 : 6,
        background: color,
        borderRadius: '50%'
      }} />
      {showLabel && <span>{LABELS[level]}</span>}
    </div>
  )
}
