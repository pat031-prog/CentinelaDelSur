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
  const dotSize = size === 'sm' ? 6 : size === 'lg' ? 10 : 8
  const fontSize = size === 'sm' ? '0.7rem' : size === 'lg' ? '0.85rem' : '0.75rem'
  const pad = size === 'sm' ? '2px 8px' : size === 'lg' ? '5px 14px' : '3px 10px'

  return (
    <span className="pill" style={{
      borderColor: color,
      padding: pad,
      gap: '5px',
    }}>
      <span style={{
        width: dotSize, height: dotSize, borderRadius: '50%',
        background: color, display: 'inline-block', flexShrink: 0,
      }} />
      {showLabel && (
        <span style={{ fontSize, fontWeight: 600, color: 'var(--text-primary)' }}>
          {LABELS[level]}
        </span>
      )}
    </span>
  )
}
