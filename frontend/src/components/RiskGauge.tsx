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
  const [progress, setProgress] = useState(0)
  const color = COLORS[level] || 'var(--text-muted)'
  const radius = size * 0.38
  const stroke = size * 0.075
  const circ = 2 * Math.PI * radius

  useEffect(() => {
    const t = setTimeout(() => setProgress(score), 80)
    return () => clearTimeout(t)
  }, [score])

  const offset = circ - (progress / 100) * circ

  return (
    <div style={{ textAlign: 'center' }}>
      {label && <div className="label" style={{ marginBottom: '0.5rem' }}>{label}</div>}
      <div style={{ position: 'relative', width: size, height: size, margin: '0 auto' }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--border)" strokeWidth={stroke} />
          <circle
            cx={size / 2} cy={size / 2} r={radius} fill="none"
            stroke={color} strokeWidth={stroke}
            strokeDasharray={circ} strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)' }}
          />
        </svg>
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}>
          <div className="stat-number" style={{ fontSize: size * 0.25, color: 'var(--text-primary)' }}>
            {Math.round(progress)}
          </div>
        </div>
      </div>
    </div>
  )
}
