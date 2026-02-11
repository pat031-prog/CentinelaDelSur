import { useEffect, useState } from 'react'

interface Commodity {
    name: string
    status: 'Critical' | 'Stable' | 'Booming' | string
    trend: 'Up' | 'Down' | 'Stable' | string
    details?: string
}

export default function CommodityTicker({ commodities }: { commodities: Commodity[] }) {
    if (!commodities || commodities.length === 0) return null

    return (
        <div className="glass-panel" style={{
            width: '100%',
            height: '36px',
            overflow: 'hidden',
            position: 'relative',
            background: 'rgba(0,0,0,0.3)',
            borderTop: '1px solid rgba(255,255,255,0.05)',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
            display: 'flex',
            alignItems: 'center'
        }}>
            {/* Label */}
            <div style={{
                padding: '0 1rem',
                height: '100%',
                display: 'flex', alignItems: 'center',
                fontSize: '0.6rem', fontWeight: 800,
                background: 'var(--bg-secondary)',
                color: 'var(--accent)',
                zIndex: 2
            }}>
                STRATEGIC_RESOURCES
            </div>

            {/* Scrolling Content */}
            <div style={{
                display: 'flex',
                whiteSpace: 'nowrap',
                animation: 'ticker 20s linear infinite',
                paddingLeft: '1rem'
            }}>
                {[...commodities, ...commodities, ...commodities].map((c, i) => {
                    let color = 'var(--text-secondary)'
                    if (c.status.toLowerCase().includes('critical') || c.trend.toLowerCase().includes('down')) color = 'var(--risk-critical)'
                    if (c.status.toLowerCase().includes('booming') || c.trend.toLowerCase().includes('up')) color = 'var(--risk-low)'

                    return (
                        <div key={i} style={{ display: 'inline-flex', alignItems: 'center', marginRight: '2rem', fontSize: '0.75rem', fontFamily: 'var(--font-data)' }}>
                            <span style={{ fontWeight: 700, marginRight: '0.4rem', color: 'var(--text-primary)' }}>{c.name.toUpperCase()}</span>
                            <span style={{ color }}>
                                {c.trend === 'Up' ? '▲' : c.trend === 'Down' ? '▼' : '◼'} {c.status.toUpperCase()}
                            </span>
                            {c.details && <span style={{ marginLeft: '0.4rem', opacity: 0.6, fontSize: '0.65rem' }}>({c.details})</span>}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
