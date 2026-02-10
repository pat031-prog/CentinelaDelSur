import { AlertLevel } from '../types'

interface DomainData {
  domain: string
  score: number
  level: AlertLevel
}

interface DomainChartProps {
  data: DomainData[]
}

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: '#22c55e',
  yellow: '#eab308',
  orange: '#f97316',
  red: '#ef4444',
  black: '#6b21a8',
}

const DOMAIN_LABELS: Record<string, string> = {
  political: 'Political',
  economic: 'Economic',
  supply_chain: 'Supply Chain',
  geopolitical: 'Geopolitical',
  climate: 'Climate',
  technology: 'Technology',
}

export default function DomainChart({ data }: DomainChartProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {data.map(item => (
        <div key={item.domain}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '0.25rem',
            fontSize: '0.85rem',
          }}>
            <span style={{ color: 'var(--text-secondary)' }}>
              {DOMAIN_LABELS[item.domain] || item.domain}
            </span>
            <span style={{
              color: LEVEL_COLORS[item.level] || 'var(--text-muted)',
              fontWeight: 600,
              fontFamily: 'monospace',
            }}>
              {item.score.toFixed(1)}
            </span>
          </div>
          <div style={{
            width: '100%',
            height: '8px',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: '4px',
            overflow: 'hidden',
          }}>
            <div style={{
              width: `${Math.min(100, item.score)}%`,
              height: '100%',
              backgroundColor: LEVEL_COLORS[item.level] || 'var(--text-muted)',
              borderRadius: '4px',
              transition: 'width 0.5s ease',
            }} />
          </div>
        </div>
      ))}
    </div>
  )
}
