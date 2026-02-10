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
  green: '#10b981',
  yellow: '#eab308',
  orange: '#f97316',
  red: '#ef4444',
  black: '#a855f7',
}

const DOMAIN_ICONS: Record<string, string> = {
  political: '⚡',
  economic: '💰',
  supply_chain: '📦',
  geopolitical: '🌐',
  climate: '🌪️',
  technology: '🤖',
}

const DOMAIN_LABELS: Record<string, string> = {
  political: 'POLITICAL',
  economic: 'ECONOMIC',
  supply_chain: 'SUPPLY CHAIN',
  geopolitical: 'GEOPOLITICAL',
  climate: 'CLIMATE',
  technology: 'TECHNOLOGY',
}

export default function DomainChart({ data }: DomainChartProps) {
  const [animated, setAnimated] = useState(false)

  useEffect(() => {
    // Trigger animation after mount
    const timer = setTimeout(() => setAnimated(true), 100)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {data.map((item, index) => {
        const color = LEVEL_COLORS[item.level] || 'var(--text-muted)'
        const width = animated ? Math.min(100, item.score) : 0

        return (
          <div key={item.domain} style={{ position: 'relative' }}>
            {/* Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.4rem',
              alignItems: 'center',
              fontFamily: 'JetBrains Mono',
              fontSize: '0.75rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                <span style={{ opacity: 0.7 }}>{DOMAIN_ICONS[item.domain] || '•'}</span>
                <span style={{ letterSpacing: '0.05em' }}>{DOMAIN_LABELS[item.domain] || item.domain.toUpperCase()}</span>
              </div>
              <span style={{
                color: color,
                fontWeight: 600,
                textShadow: `0 0 5px ${color}40`
              }}>
                {item.score.toFixed(1)}
              </span>
            </div>

            {/* Bar Background */}
            <div style={{
              width: '100%',
              height: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '2px',
              overflow: 'hidden',
              position: 'relative',
            }}>
              {/* Animated Bar */}
              <div style={{
                width: `${width}%`,
                height: '100%',
                backgroundColor: color,
                boxShadow: `0 0 8px ${color}60`,
                borderRadius: '2px',
                transition: `width 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 100}ms`,
                position: 'relative',
              }}>
                {/* Shine effect */}
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                  transform: 'skewX(-20deg)',
                }} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
