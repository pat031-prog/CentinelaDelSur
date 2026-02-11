import { useEffect, useState } from 'react'
import { AlertLevel } from '../types'

interface Props {
  score: number
  level: AlertLevel
  label?: string
  size?: number
}

const COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-green)',
  yellow: 'var(--risk-yellow)',
  orange: 'var(--risk-orange)',
  red: 'var(--risk-red)',
  black: 'var(--risk-black)',
}

export default function RiskGauge({ score, level, label, size = 140 }: Props) {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const t = setTimeout(() => setCurrent(score), 100)
    return () => clearTimeout(t)
  }, [score])

  const color = COLORS[level] || 'var(--text-muted)'

  return (
    <div style={{ textAlign: 'center', border: '1px solid var(--border)', padding: '1.5rem', background: 'var(--bg-card)' }}>
      {label && (
        <div className="label-archive" style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
          {label}
        </div>
      )}

      <div style={{
        fontFamily: 'var(--font-serif)',
        fontSize: '4rem',
        fontWeight: 700,
        lineHeight: 0.9,
        color: 'var(--text-primary)',
        marginTop: '0.5rem'
      }}>
        {Math.round(current)}
      </div>

      <div style={{
        marginTop: '0.5rem',
        height: '4px',
        width: '100%',
        background: 'var(--border-light)',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          left: 0, top: 0, bottom: 0,
          width: `${current}%`,
          background: color,
          transition: 'width 1s ease-out'
        }} />
      </div>
    </div>
  )
}
