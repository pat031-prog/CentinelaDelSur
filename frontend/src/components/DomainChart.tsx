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
    <div style={{ display: 'flex', flexDirection: 'column', borderTop: '1px solid var(--border)' }}>
      {data.map((d, i) => {
        const color = COLORS[d.level] || 'var(--text-muted)'
        const w = show ? Math.min(100, d.score) : 0
        return (
          <div key={d.domain} style={{
            padding: '0.75rem 0',
            borderBottom: '1px solid var(--border-light)',
            display: 'grid',
            gridTemplateColumns: '1fr 60px',
            gap: '1rem',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>{NAMES[d.domain] || d.domain}</span>
              </div>
              <div style={{ height: '8px', width: '100%', background: 'rgba(0,0,0,0.05)', position: 'relative' }}>
                <div style={{
                  position: 'absolute',
                  left: 0, top: 0, bottom: 0,
                  width: `${w}%`,
                  background: color,
                  transition: `width 0.5s ease-out ${i * 50}ms`
                }} />
              </div>
            </div>
            <div style={{
              textAlign: 'right',
              fontFamily: 'var(--font-serif)',
              fontWeight: 700,
              fontSize: '1.1rem',
              color: color
            }}>
              {d.score.toFixed(0)}
            </div>
          </div>
        )
      })}
    </div>
  )
}
