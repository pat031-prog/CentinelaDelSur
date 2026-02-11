import { Zap, Activity, Cpu } from 'lucide-react'

interface TechRadar {
    level: string
    highlights: string[]
}

export default function TechSingularityPanel({ data }: { data: TechRadar }) {
    const isHighTech = data.level.toLowerCase().includes('advanced') || data.level.toLowerCase().includes('emerging')

    return (
        <div className="grid-card glass-panel" style={{
            position: 'relative',
            overflow: 'hidden',
            borderColor: isHighTech ? 'var(--accent)' : 'var(--border-color)'
        }}>
            {/* Header */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                paddingBottom: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.1)'
            }}>
                <div className="t-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: isHighTech ? 'var(--accent)' : 'var(--text-secondary)' }}>
                    <Cpu size={14} />
                    <span>TECH_SINGULARITY_RADAR</span>
                </div>
                <div style={{
                    fontSize: '0.6rem', padding: '2px 6px', borderRadius: '4px',
                    background: isHighTech ? 'var(--accent)' : 'transparent',
                    color: isHighTech ? '#000' : 'var(--text-dim)',
                    fontWeight: 700, letterSpacing: '0.05em'
                }}>
                    {data.level.toUpperCase()}
                </div>
            </div>

            {/* Biometric/Cell Content */}
            <div style={{ paddingTop: '1rem', position: 'relative', zIndex: 1 }}>
                {data.highlights.map((item, i) => (
                    <div key={i} style={{
                        marginBottom: '0.75rem',
                        paddingLeft: '0.75rem',
                        borderLeft: '2px solid rgba(255,255,255,0.1)',
                        transition: 'border-color 0.3s ease'
                    }}
                        className="tech-item-hover">
                        <div style={{ fontSize: '0.75rem', lineHeight: 1.4 }}>{item}</div>
                    </div>
                ))}

                {data.highlights.length === 0 && (
                    <div style={{ fontSize: '0.75rem', opacity: 0.5, fontStyle: 'italic' }}>No hay señales tecnológicas detectadas.</div>
                )}
            </div>

            {/* Decorative DNA/Pulse Animation */}
            <div style={{
                position: 'absolute', bottom: '10px', right: '10px',
                opacity: 0.1, pointerEvents: 'none'
            }}>
                <Activity size={64} style={{ color: isHighTech ? 'var(--accent)' : 'var(--text-dim)' }} />
            </div>

            {/* CSS for hover effect */}
            <style>{`
        .tech-item-hover:hover {
            border-left-color: var(--accent) !important;
            background: linear-gradient(90deg, rgba(255,255,255,0.03), transparent);
        }
      `}</style>
        </div>
    )
}
