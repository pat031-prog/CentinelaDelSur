import { useRef, useEffect } from 'react'

interface GeopoliticsRadarProps {
    score: number // -100 (USA) to +100 (China/Russia)
    description?: string
}

export default function GeopoliticsRadar({ score, description }: GeopoliticsRadarProps) {
    // Normalize score to 0-100% for CSS positioning
    // -100 => 0% (Left/USA)
    // 0 => 50% (Neutral)
    // +100 => 100% (Right/China)
    const position = Math.min(100, Math.max(0, (score + 100) / 2))

    // Dynamic color: Blue (West) -> Purple (Neutral) -> Red (East)
    const getGradient = (pos: number) => {
        if (pos < 30) return 'linear-gradient(90deg, #0055ff, #00aaff)' // Western
        if (pos > 70) return 'linear-gradient(90deg, #ff4444, #ff0000)' // Eastern
        return 'linear-gradient(90deg, #00aaff, #ff4444)' // Mixed/Tension
    }

    return (
        <div className="grid-card glass-panel" style={{ position: 'relative', overflow: 'hidden', padding: '1.5rem' }}>
            <div className="t-label" style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>Alineación Geopolítica</span>
                <span style={{ fontSize: '0.65rem', opacity: 0.7, letterSpacing: '0.1em' }}>TENSION_AXIS</span>
            </div>

            <div style={{ position: 'relative', height: '60px', marginTop: '0.5rem' }}>
                {/* Background Track */}
                <div style={{
                    position: 'absolute', top: '50%', left: 0, right: 0, height: '2px',
                    background: 'rgba(255,255,255,0.1)', transform: 'translateY(-50%)'
                }} />

                {/* Labels */}
                <div style={{ position: 'absolute', left: 0, top: '50%', transform: 'translateY(-140%)', fontSize: '0.6rem', color: '#00aaff', fontWeight: 700 }}>
                    WESTERN BLOC
                </div>
                <div style={{ position: 'absolute', right: 0, top: '50%', transform: 'translateY(-140%)', fontSize: '0.6rem', color: '#ff4444', fontWeight: 700 }}>
                    EASTERN BLOC
                </div>

                {/* Tension Bar (The "Cursor") */}
                <div style={{
                    position: 'absolute',
                    left: `${position}%`,
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '12px',
                    height: '24px',
                    background: getGradient(position),
                    boxShadow: `0 0 15px ${position > 50 ? '#ff4444' : '#00aaff'}`,
                    borderRadius: '2px',
                    transition: 'all 1s cubic-bezier(0.22, 1, 0.36, 1)'
                }} />

                {/* Connecting Line to Cursor */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: `${Math.abs(position - 50)}%`,
                    height: '2px',
                    background: position > 50 ? 'linear-gradient(90deg, transparent, #ff4444)' : 'linear-gradient(-90deg, transparent, #00aaff)',
                    transform: `translateY(-50%) ${position < 50 ? 'scaleX(-1)' : ''}`,
                    transformOrigin: 'left',
                    opacity: 0.6
                }} />
            </div>

            {/* Description */}
            <div style={{
                marginTop: '0.5rem',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                borderLeft: `2px solid ${position > 50 ? '#ff4444' : '#00aaff'}`,
                paddingLeft: '0.75rem',
                lineHeight: 1.4
            }}>
                {description || "Datos insuficientes para determinar alineación estratégica."}
            </div>

            {/* Grid Overlay Effect */}
            <div style={{
                position: 'absolute', inset: 0, pointerEvents: 'none',
                backgroundImage: 'linear-gradient(VAR(--border-light) 1px, transparent 1px), linear-gradient(90deg, VAR(--border-light) 1px, transparent 1px)',
                backgroundSize: '20px 20px',
                opacity: 0.03
            }} />
        </div>
    )
}
