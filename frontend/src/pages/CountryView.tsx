import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import AlertBadge from '../components/AlertBadge'
import RiskGauge from '../components/RiskGauge'
import DomainChart from '../components/DomainChart'

export default function CountryView() {
  const { code } = useParams<{ code: string }>()
  const [data, setData] = useState<any>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    if (!code) return
    async function load() {
      try {
        const result = await api.getCountry(code!)
        setData(result)
      } catch (e) {
        console.error('Failed to load country:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [code])

  const runAnalysis = async () => {
    if (!code) return
    setAnalyzing(true)
    try {
      const result = await api.analyzeCountry(code)
      setAnalysis(result)
    } catch (e) {
      console.error('Analysis failed:', e)
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <LoadingScreen />

  if (!data) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--red)' }}>
        DATA UPLINK FAILED: TARGET NOT FOUND
      </div>
    )
  }

  const risk = data.risk_assessment || {}
  const domains = risk.domains || {}
  const domainData = Object.entries(domains).map(([domain, info]: [string, any]) => ({
    domain,
    score: info.score || 0,
    level: info.level || 'green',
  }))

  return (
    <div className="animate-fade-in-up">
      <Link to="/" style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        color: 'var(--text-muted)',
        fontSize: '0.85rem',
        marginBottom: '1.5rem',
        fontFamily: 'JetBrains Mono'
      }}>
        <span style={{ fontSize: '1.2rem' }}>‹</span> RETURN TO DASHBOARD
      </Link>

      {/* Hero Banner */}
      <div className="glass-panel" style={{
        padding: '2rem',
        borderRadius: '12px',
        marginBottom: '2rem',
        background: 'linear-gradient(90deg, rgba(16, 24, 39, 0.9) 0%, rgba(16, 24, 39, 0.6) 100%)',
        borderLeft: `4px solid ${getLevelColor(risk.level)}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <span style={{
              fontFamily: 'JetBrains Mono',
              color: 'var(--accent)',
              background: 'rgba(56, 189, 248, 0.1)',
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '0.85rem'
            }}>
              {code}
            </span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', letterSpacing: '0.05em' }}>
              {data.region.toUpperCase()}
            </span>
          </div>
          <h1 style={{
            fontSize: '3rem',
            margin: 0,
            lineHeight: 1,
            letterSpacing: '-0.02em',
            textShadow: '0 0 20px rgba(0,0,0,0.5)'
          }}>
            {data.name}
          </h1>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontFamily: 'JetBrains Mono' }}>Current Threat Level</div>
          <AlertBadge level={risk.level} size="lg" />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem' }}>
        {/* Left Column: Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Risk Gauge Panel */}
          <div className="glass-panel" style={{ padding: '2rem', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{
              fontSize: '0.9rem',
              color: 'var(--text-secondary)',
              marginBottom: '1.5rem',
              fontFamily: 'JetBrains Mono',
              letterSpacing: '0.1em'
            }}>
              SYSTEMIC FRAGILITY
            </h3>
            <RiskGauge score={risk.score || 0} level={risk.level || 'green'} size={180} />

            <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
              <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem', textAlign: 'left' }}>
                CRISIS PROBABILITY FORECAST
              </h4>
              {['30_days', '60_days', '90_days'].map(period => {
                const prob = risk.crisis_probability?.[period]
                if (!prob) return null
                return (
                  <div key={period} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.85rem',
                    marginBottom: '0.75rem',
                    fontFamily: 'JetBrains Mono'
                  }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{period.replace('_', ' ').toUpperCase()}</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                      {(prob.probability * 100).toFixed(1)}%
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Key Stats Panel */}
          <div className="glass-panel" style={{ padding: '1.5rem', borderRadius: '12px' }}>
            <StatRow label="POPULATION" value={`${(data.population / 1e6).toFixed(1)}M`} />
            <StatRow label="GDP (USD)" value={`$${(data.gdp_usd / 1e9).toFixed(0)}B`} />
            <StatRow label="CAPITAL" value={data.capital} />
            <StatRow label="SUBREGION" value={data.subregion} />
          </div>
        </div>

        {/* Right Column: Analysis */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Domain Breakdown */}
          <div className="glass-panel" style={{ padding: '2rem', borderRadius: '12px' }}>
            <h3 style={{
              fontSize: '1rem',
              marginBottom: '1.5rem',
              color: 'var(--text-secondary)',
              fontFamily: 'JetBrains Mono',
              letterSpacing: '0.05em'
            }}>
              DOMAIN VULNERABILITY MATRIX
            </h3>
            <DomainChart data={domainData} />
          </div>

          {/* Deep Analysis Section */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{
                fontSize: '1.2rem',
                color: 'var(--text-primary)',
                fontFamily: 'JetBrains Mono',
                letterSpacing: '0.05em'
              }}>
                INTELLIGENCE REPORT
              </h3>

              <button
                onClick={runAnalysis}
                disabled={analyzing}
                style={{
                  background: analyzing ? 'rgba(56, 189, 248, 0.1)' : 'var(--accent)',
                  color: analyzing ? 'var(--text-muted)' : '#fff',
                  border: '1px solid var(--border)',
                  borderRadius: '6px',
                  padding: '0.75rem 1.5rem',
                  fontSize: '0.85rem',
                  fontFamily: 'JetBrains Mono',
                  cursor: analyzing ? 'wait' : 'pointer',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  transition: 'all 0.2s ease',
                  boxShadow: analyzing ? 'none' : '0 0 15px var(--accent-glow)'
                }}
              >
                {analyzing && <div className="status-dot" style={{ background: 'var(--text-muted)', animation: 'blink 1s infinite' }} />}
                {analyzing ? 'GENERATING...' : 'GENERATE DEEP ANALYSIS'}
              </button>
            </div>

            {analyzing && (
              <div style={{
                padding: '4rem',
                textAlign: 'center',
                border: '1px dashed var(--border)',
                borderRadius: '8px',
                background: 'rgba(0,0,0,0.2)'
              }}>
                <div style={{ width: '60%', height: '2px', background: 'var(--border)', margin: '0 auto 1rem', overflow: 'hidden', position: 'relative' }}>
                  <div style={{ position: 'absolute', inset: 0, width: '50%', background: 'var(--accent)', animation: 'scan-line 1s infinite linear' }} />
                </div>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  PROCESSING NEURAL VECTORS...
                </div>
              </div>
            )}

            {analysis && !analyzing && (
              <div className="glass-panel animate-fade-in-up" style={{ padding: '2.5rem', borderRadius: '12px' }}>
                <SimpleMarkdown content={analysis.report_text} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatRow({ label, value }: { label: string, value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>{label}</span>
      <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 500 }}>{value}</span>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh'
    }}>
      <div style={{ width: '40px', height: '40px', border: '3px solid var(--accent)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
      <div style={{ marginTop: '1rem', fontFamily: 'JetBrains Mono', fontSize: '0.85rem', color: 'var(--text-muted)' }}>ACCESSING SECURE LINK...</div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

function getLevelColor(level: string): string {
  const colors: any = { green: '#10b981', yellow: '#eab308', orange: '#f97316', red: '#ef4444', black: '#a855f7' }
  return colors[level] || '#64748b'
}

// Simple Markdown Renderer
function SimpleMarkdown({ content }: { content: string }) {
  if (!content) return null

  // Split by double newline to get paragraphs
  const parts = content.split('\n\n')

  return (
    <div style={{ fontFamily: 'Inter', lineHeight: 1.7, color: 'var(--text-primary)' }}>
      {parts.map((part, i) => {
        // Headers
        if (part.startsWith('#')) {
          const level = part.match(/^#+/)?.[0].length || 0
          const text = part.replace(/^#+\s/, '')
          const fontSize = level === 1 ? '1.8rem' : level === 2 ? '1.4rem' : '1.1rem'
          const color = level === 1 ? 'var(--accent)' : 'var(--text-primary)'

          return (
            <h1 key={i} style={{
              fontSize,
              color,
              marginTop: '1.5rem',
              marginBottom: '1rem',
              fontWeight: 700,
              borderBottom: level < 3 ? '1px solid var(--border)' : 'none',
              paddingBottom: level < 3 ? '0.5rem' : '0'
            }}>
              {text}
            </h1>
          )
        }

        // Lists
        if (part.trim().startsWith('- ') || part.trim().startsWith('* ')) {
          const items = part.split('\n').filter(l => l.trim())
          return (
            <ul key={i} style={{ paddingLeft: '1.5rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              {items.map((item, j) => (
                <li key={j} style={{ marginBottom: '0.5rem' }}>
                  {item.replace(/^[-*]\s/, '')
                    .replace(/\*\*(.*?)\*\*/g, (_, p1) => `<b>${p1}</b>`)}
                </li>
              ))}
            </ul>
          )
        }

        // Standard Paragraphs with Bold support
        return (
          <p key={i} style={{ marginBottom: '1rem', fontSize: '1rem' }}
            dangerouslySetInnerHTML={{
              __html: part.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--text-primary); font-weight:600">$1</strong>')
            }}
          />
        )
      })}
    </div>
  )
}
