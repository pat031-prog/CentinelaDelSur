import { useEffect, useState } from 'react'
import { AlertLevel } from '../types'

interface DomainData {
  domain: string
  score: number
  level: AlertLevel
}

interface Props {
  data: DomainData[]
}

const COLORS: Record<AlertLevel, string> = {
  green: 'var(--risk-green)',
  yellow: 'var(--risk-yellow)',
  orange: 'var(--risk-orange)',
  red: 'var(--risk-red)',
  black: 'var(--risk-black)',
}

const NAMES: Record<string, string> = {
  political: 'Político',
  economic: 'Económico',
  supply_chain: 'Cadena de Suministro',
  geopolitical: 'Geopolítico',
  climate: 'Climático',
  technology: 'Tecnología',
}

export default function DomainChart({ data }: Props) {
  const [show, setShow] = useState(false)
  useEffect(() => { setTimeout(() => setShow(true), 60) }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {data.map((d, i) => {
        const color = COLORS[d.level] || 'var(--text-muted)'
        const w = show ? Math.min(100, d.score) : 0
        return (
          <div key={d.domain}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: '0.85rem' }}>
              <span style={{ fontWeight: 600 }}>{NAMES[d.domain] || d.domain}</span>
              <span style={{ fontWeight: 700, color }}>{d.score.toFixed(1)}</span>
            </div>
            <div style={{ height: 6, borderRadius: 3, background: 'var(--border)', overflow: 'hidden' }}>
              <div style={{
                width: `${w}%`, height: '100%', background: color, borderRadius: 3,
                transition: `width 0.7s cubic-bezier(0.4,0,0.2,1) ${i * 80}ms`,
              }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}
