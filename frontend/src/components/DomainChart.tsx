import { AlertLevel } from '../types'
import { useEffect, useState } from 'react'

interface DomainData {
  domain: string
  score: number
  level: AlertLevel
}

interface DomainChartProps {
  data: DomainData[]
}

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-low)',
  yellow: 'var(--risk-med)',
  orange: 'var(--risk-med)',
  red: 'var(--risk-high)',
  black: 'var(--risk-black)',
}

const DOMAIN_LABELS: Record<string, string> = {
  political: 'Political Stability',
  economic: 'Economic Health',
  supply_chain: 'Supply Chain',
  geopolitical: 'Geopolitics',
  climate: 'Climate Risk',
  technology: 'Cyber/Tech',
}

export default function DomainChart({ data }: DomainChartProps) {
  const [animated, setAnimated] = useState(false)

  useEffect(() => {
    // Trigger animation after mount
    const timer = setTimeout(() => setAnimated(true), 100)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {data.map((item, index) => {
        const color = LEVEL_COLORS[item.level] || 'var(--text-secondary)'
        const width = animated ? Math.min(100, item.score) : 0

        return (
          <div key={item.domain} style={{ position: 'relative' }}>
            {/* Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.4rem',
              alignItems: 'center',
              fontSize: '0.85rem',
            }}>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                {DOMAIN_LABELS[item.domain] || item.domain}
              </span>
              <span style={{
                color: color,
                fontWeight: 700,
                fontFamily: 'JetBrains Mono'
              }}>
                {item.score.toFixed(1)}
              </span>
            </div>

            {/* Bar Background */}
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#f1f5f9',
              borderRadius: '4px',
              overflow: 'hidden',
              position: 'relative',
            }}>
              {/* Animated Bar */}
              <div style={{
                width: `${width}%`,
                height: '100%',
                backgroundColor: color,
                borderRadius: '4px',
                transition: `width 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 100}ms`,
              }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}
