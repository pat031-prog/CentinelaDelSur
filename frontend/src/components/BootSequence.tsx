import { useState, useEffect } from 'react'

export default function BootSequence({ onComplete }: { onComplete: () => void }) {
    const [logs, setLogs] = useState<string[]>([])
    const [progress, setProgress] = useState(0)

    const bootSteps = [
        "INITIALIZING_KERNEL...",
        "LOADING_GEOPOLITICAL_VECTORS...",
        "ESTABLISHING_SECURE_UPLINK...",
        "SYNCING_SATELLITE_TELEMETRY...",
        "DECRYPTING_OFFICIAL_CHANNELS...",
        "LOADING_AI_NEURAL_NODES...",
        "BUFFERING_REALTIME_STREAMS...",
        "SYSTEM_READY."
    ]

    useEffect(() => {
        let stepIndex = 0
        const interval = setInterval(() => {
            if (stepIndex >= bootSteps.length) {
                clearInterval(interval)
                setTimeout(onComplete, 800) // Small delay after completion
                return
            }

            setLogs(prev => [...prev, bootSteps[stepIndex]])
            setProgress(((stepIndex + 1) / bootSteps.length) * 100)
            stepIndex++
        }, 400) // Speed of boot text

        return () => clearInterval(interval)
    }, [])

    return (
        <div style={{
            position: 'fixed',
            inset: 0,
            background: '#000',
            color: 'var(--accent)',
            fontFamily: 'monospace',
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'flex-end',
            zIndex: 9999
        }}>
            <div style={{ marginBottom: '2rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '1rem', textShadow: '0 0 10px var(--accent)' }}>
                    ATALAYA <span style={{ color: '#fff' }}>OS</span> v2.0
                </div>
                <div style={{ width: '300px', height: '4px', background: '#333', marginBottom: '1rem' }}>
                    <div style={{ width: `${progress}%`, height: '100%', background: 'var(--accent)', transition: 'width 0.2s' }} />
                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem', opacity: 0.8 }}>
                {logs.map((log, i) => (
                    <div key={i} className="typewriter-line">
                        <span style={{ color: '#555' }}>[{new Date().toLocaleTimeString()}]</span> {log}
                    </div>
                ))}
            </div>

            <div className="crt-overlay" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />
        </div>
    )
}
