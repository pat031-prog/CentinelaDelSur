import { useEffect, useState } from 'react'
import { AlertLevel } from '../types'

interface RiskGaugeProps {
  score: number
  level: AlertLevel
  label?: string
  size?: number
}

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-low)',
  yellow: 'var(--risk-med)',
  orange: 'var(--risk-med)',
  red: 'var(--risk-high)',
  black: 'var(--risk-black)',
}

export default function RiskGauge({ score, level, label, size = 120 }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const color = LEVEL_COLORS[level] || 'var(--text-secondary)'

  // Calculate circumference
  const radius = size * 0.4
  const strokeWidth = size * 0.08
  const circumference = 2 * Math.PI * radius

  // Animation effect
  const [offset, setOffset] = useState(circumference)

  useEffect(() => {
    // Animate the arc
    const targetOffset = circumference - (score / 100) * circumference
    setTimeout(() => setOffset(targetOffset), 100)

    // Animate the number
    let start = 0
    const duration = 1500
    const stepTime = 20
    const steps = duration / stepTime
    const increment = score / steps

    const timer = setInterval(() => {
      start += increment
      if (start >= score) {
        setAnimatedScore(score)
        clearInterval(timer)
      } else {
        setAnimatedScore(start)
      }
    }, stepTime)

    return () => clearInterval(timer)
  }, [score, circumference])

  return (
    <div style={{ textAlign: 'center', position: 'relative' }}>
      {label && (
        <div style={{
          color: 'var(--text-secondary)',
          fontSize: '0.75rem',
          marginBottom: '0.5rem',
          fontFamily: 'JetBrains Mono',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          fontWeight: 600
        }}>
          {label}
        </div>
      )}

      <div style={{ width: size, height: size, margin: '0 auto', position: 'relative' }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle - Darker for Light Mode */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
          />

          {/* Animated Value arc */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          />
        </svg>

        {/* Center Text */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}>
          <div style={{
            fontSize: `${size * 0.25}px`,
            fontWeight: 800,
            fontFamily: 'JetBrains Mono',
            color: 'var(--text-primary)',
            lineHeight: 1
          }}>
            {Math.round(animatedScore)}
          </div>
        </div>
      </div>
    </div>
  )
}
