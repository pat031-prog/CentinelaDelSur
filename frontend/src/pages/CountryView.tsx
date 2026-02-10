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

  if (loading) return <div className="p-8 text-center">Loading Dossier...</div>

  if (!data) return <div className="p-8 text-center text-red-600">DOSSIER NOT FOUND</div>

  const risk = data.risk_assessment || {}
  const domains = risk.domains || {}
  const domainData = Object.entries(domains).map(([domain, info]: [string, any]) => ({
    domain,
    score: info.score || 0,
    level: info.level || 'green',
  }))

  return (
    <div className="animate-enter">
      <Link to="/" style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        color: 'var(--text-secondary)',
        fontSize: '0.85rem',
        marginBottom: '1.5rem',
        textDecoration: 'none',
        fontWeight: 500
      }}>
        ← Back to Board
      </Link>

      {/* Hero Banner - Bento Style */}
      <div className="bento-card" style={{
        padding: '2rem',
        marginBottom: '2rem',
        background: 'white',
        borderLeft: `6px solid ${getLevelColor(risk.level)}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <span style={{
              fontFamily: 'JetBrains Mono',
              color: 'var(--text-secondary)',
              background: '#f1f5f9',
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '0.85rem',
              fontWeight: 600
            }}>
              {code}
            </span>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', letterSpacing: '0.05em', textTransform: 'uppercase', fontWeight: 600 }}>
              {data.region}
            </span>
          </div>
          <h1 style={{ fontSize: '2.5rem', margin: 0, lineHeight: 1, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
            {data.name}
          </h1>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 500 }}>CURRENT THREAT STATUS</div>
          <AlertBadge level={risk.level} size="lg" />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem' }}>
        {/* Left Column: Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          <div className="bento-card" style={{ padding: '2rem', textAlign: 'center' }}>
            <div className="bento-title" style={{ justifyContent: 'center' }}>FRAGILITY INDEX</div>
            <RiskGauge score={risk.score || 0} level={risk.level || 'green'} size={180} />

            <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
              <div className="bento-title">CRISIS FORECAST</div>
              {['30_days', '60_days', '90_days'].map(period => {
                const prob = risk.crisis_probability?.[period]
                if (!prob) return null
                return (
                  <div key={period} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.85rem',
                    marginBottom: '0.75rem',
                    padding: '0.5rem',
                    background: '#f8fafc',
                    borderRadius: '6px'
                  }}>
                    <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>{period.replace('_', ' ').toUpperCase()}</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 700, fontFamily: 'JetBrains Mono' }}>
                      {(prob.probability * 100).toFixed(1)}%
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="bento-card">
            <div className="bento-title">KEY METRICS</div>
            <StatRow label="POPULATION" value={`${(data.population / 1e6).toFixed(1)}M`} />
            <StatRow label="GDP (USD)" value={`$${(data.gdp_usd / 1e9).toFixed(0)}B`} />
            <StatRow label="CAPITAL" value={data.capital} />
          </div>
        </div>

        {/* Right Column: Analysis */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          <div className="bento-card">
            <div className="bento-title">DOMAIN BREAKDOWN</div>
            <DomainChart data={domainData} />
          </div>

          <div className="bento-card" style={{ minHeight: '400px' }}>
            <div className="bento-title">
              <span>INTELLIGENCE REPORT</span>
              <button
                onClick={runAnalysis}
                disabled={analyzing}
                style={{
                  background: analyzing ? '#e2e8f0' : 'var(--text-primary)',
                  color: analyzing ? 'var(--text-secondary)' : 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '0.5rem 1rem',
                  fontSize: '0.85rem',
                  cursor: analyzing ? 'wait' : 'pointer',
                  fontWeight: 600,
                  transition: 'all 0.2s'
                }}
              >
                {analyzing ? 'GENERATING...' : 'GENERATE ANALYSIS'}
              </button>
            </div>

            {analysis && !analyzing && (
              <div style={{
                background: '#fcfcfc',
                padding: '2rem',
                borderRadius: '8px',
                border: '1px solid #f1f5f9',
                fontFamily: 'IBM Plex serif, Georgia, serif' // Paper report feel
              }}>
                <SimpleMarkdown content={analysis.report_text} />
              </div>
            )}

            {!analysis && !analyzing && (
              <div style={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-secondary)',
                opacity: 0.5,
                fontStyle: 'italic'
              }}>
                Select "Generate Analysis" to create a new intelligence dossier.
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
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid #f1f5f9' }}>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>{label}</span>
      <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontFamily: 'JetBrains Mono', fontWeight: 500 }}>{value}</span>
    </div>
  )
}

function getLevelColor(level: string): string {
  const colors: any = { green: '#10b981', yellow: '#f59e0b', orange: '#f97316', red: '#dc2626', black: '#7c3aed' }
  return colors[level] || '#64748b'
}

function SimpleMarkdown({ content }: { content: string }) {
  if (!content) return null
  const parts = content.split('\n\n')
  return (
    <div style={{ lineHeight: 1.8, color: '#334155' }}>
      {parts.map((part, i) => {
        if (part.startsWith('#')) {
          const level = part.match(/^#+/)?.[0].length || 0
          const text = part.replace(/^#+\s/, '')
          return <h3 key={i} style={{ fontSize: level === 1 ? '1.5rem' : '1.1rem', color: '#0f172a', marginTop: '1.5rem', marginBottom: '0.75rem', fontWeight: 700 }}>{text}</h3>
        }
        if (part.trim().startsWith('- ')) {
          const items = part.split('\n').filter(l => l.trim())
          return <ul key={i} style={{ paddingLeft: '1.5rem', marginBottom: '1rem' }}>{items.map((item, j) => <li key={j}>{item.replace(/^-\s/, '')}</li>)}</ul>
        }
        return <p key={i} style={{ marginBottom: '1rem' }}>{part}</p>
      })}
    </div>
  )
}
