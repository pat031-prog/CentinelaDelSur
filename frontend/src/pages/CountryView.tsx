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

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>Loading...</div>
  }

  if (!data) {
    return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--red)' }}>Country not found</div>
  }

  const risk = data.risk_assessment || {}
  const domains = risk.domains || {}
  const domainData = Object.entries(domains).map(([domain, info]: [string, any]) => ({
    domain,
    score: info.score || 0,
    level: info.level || 'green',
  }))

  return (
    <div>
      <Link to="/" style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        &larr; Back to Dashboard
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '1rem 0 2rem' }}>
        <h1 style={{ fontSize: '2rem', margin: 0 }}>{data.name}</h1>
        <span style={{ color: 'var(--text-muted)' }}>({code})</span>
        {risk.level && <AlertBadge level={risk.level} size="lg" />}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem' }}>
        {/* Left: Risk overview */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '1.5rem',
          }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              Systemic Fragility Index
            </h3>
            <RiskGauge score={risk.score || 0} level={risk.level || 'green'} />

            {risk.crisis_probability && (
              <div style={{ marginTop: '1.5rem' }}>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Crisis Probability
                </h4>
                {['30_days', '60_days', '90_days'].map(period => {
                  const prob = risk.crisis_probability[period]
                  if (!prob) return null
                  return (
                    <div key={period} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.85rem',
                      padding: '0.25rem 0',
                    }}>
                      <span style={{ color: 'var(--text-muted)' }}>{period.replace('_', ' ')}:</span>
                      <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>
                        {(prob.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '1.5rem',
          }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              Country Info
            </h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <p>Capital: {data.capital}</p>
              <p>Region: {data.region}</p>
              <p>Population: {(data.population / 1e6).toFixed(1)}M</p>
              <p>GDP: ${(data.gdp_usd / 1e9).toFixed(0)}B USD</p>
            </div>
          </div>
        </div>

        {/* Right: Domain analysis */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '1.5rem',
          }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              Risk by Domain
            </h3>
            <DomainChart data={domainData} />
          </div>

          <button
            onClick={runAnalysis}
            disabled={analyzing}
            style={{
              background: analyzing ? 'var(--bg-secondary)' : 'var(--accent)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '0.75rem 1.5rem',
              fontSize: '0.9rem',
              cursor: analyzing ? 'wait' : 'pointer',
              fontWeight: 600,
            }}
          >
            {analyzing ? 'Generating Deep Analysis...' : 'Generate Deep Analysis'}
          </button>

          {analysis && (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '1.5rem',
            }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                ATALAYA Analysis Report
              </h3>
              <pre style={{
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                color: 'var(--text-primary)',
                lineHeight: 1.6,
                maxHeight: '600px',
                overflow: 'auto',
              }}>
                {analysis.report_text}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
