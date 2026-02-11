import { useEffect, useState } from 'react'
import { AlertLevel } from '../types'

interface Props {
  score: number
  level: AlertLevel
  label?: string
  size?: number
}

const COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-low)',
  yellow: 'var(--risk-medium)',
  orange: 'var(--risk-high)',
  red: 'var(--risk-critical)',
  black: 'var(--text-primary)',
}

export default function RiskGauge({ score, level, label, size = 140 }: Props) {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const t = setTimeout(() => setCurrent(score), 100)
    return () => clearTimeout(t)
  }, [score])

  const color = COLORS[level] || 'var(--text-muted)'

  return (
    <div style={{ textAlign: 'center' }}>
      {label && (
        <div className="t-label" style={{ marginBottom: '0.5rem' }}>{label}</div>
      )}

      <div style={{
        fontFamily: 'var(--font-display)',
        fontSize: '3.5rem',
        fontWeight: 700,
        lineHeight: 0.9,
        color: 'var(--text-primary)',
        letterSpacing: '-0.03em'
      }}>
        {Math.round(current)}
      </div>

      <div style={{
        marginTop: '0.75rem',
        height: '4px',
        width: '100%',
        maxWidth: '120px',
        margin: '0.75rem auto 0',
        background: 'var(--border-color)',
        borderRadius: '2px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${current}%`,
          height: '100%',
          background: color,
          borderRadius: '2px',
          transition: 'width 1s ease-out'
        }} />
      </div>
    </div>
  )
}
