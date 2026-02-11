import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface MarketItem {
    pair?: string
    name?: string
    price?: number
    value?: number
    rate?: number
    change: number
    unit?: string
}

export default function MarketTicker() {
    const [items, setItems] = useState<MarketItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadMarketData() {
            try {
                const [fx, comm] = await Promise.all([
                    api.getMarketFX(),
                    api.getMarketCommodities()
                ])

                // Combine and limit items for the ticker
                const fxItems = (fx.rates || []).slice(0, 4)
                const commItems = (comm.commodities || []).slice(0, 4)

                setItems([...fxItems, ...commItems])
            } catch (e) {
                console.error("Market data fetch failed:", e)
            } finally {
                setLoading(false)
            }
        }

        loadMarketData()
        // Refresh every 5 minutes
        const interval = setInterval(loadMarketData, 5 * 60 * 1000)
        return () => clearInterval(interval)
    }, [])

    if (loading || items.length === 0) return null

    return (
        <div style={{
            background: 'var(--bg-card)',
            borderBottom: '1px solid var(--border-color)',
            padding: '0.4rem 0',
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            display: 'flex',
            alignItems: 'center',
            height: '32px'
        }}>
            <div style={{
                display: 'flex',
                animation: 'ticker 30s linear infinite',
                gap: '2rem',
                paddingLeft: '1rem'
            }}>
                {/* Double the items for seamless loop */}
                {[...items, ...items].map((item, i) => {
                    const label = item.pair || item.name
                    const val = item.rate || item.value || item.price
                    const change = item.change
                    const isPos = change >= 0

                    return (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.7rem', fontFamily: 'var(--font-data)' }}>
                            <span style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>{label}</span>
                            <span style={{ color: 'var(--text-primary)' }}>
                                {/* Format logic: decimals depend on value magnitude */}
                                {typeof val === 'number' ? val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 }) : val}
                            </span>
                            <span style={{
                                color: isPos ? 'var(--risk-low)' : 'var(--risk-high)',
                                display: 'flex',
                                alignItems: 'center'
                            }}>
                                {isPos ? '▲' : '▼'} {Math.abs(change).toFixed(2)}%
                            </span>
                        </div>
                    )
                })}
            </div>
            <style>{`
        @keyframes ticker {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
        </div>
    )
}
