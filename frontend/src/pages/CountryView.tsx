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
        const res = await api.getCountry(code!)
        setData(res)
      } catch (e) {
        console.error(e)
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
      const res = await api.analyzeCountry(code)
      setAnalysis(res)
    } catch (e) {
      console.error(e)
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Loading dossier...</div>
  if (!data) return <div style={{ padding: '3rem', color: 'var(--risk-red)' }}>Dossier not found</div>

  const risk = data.risk_assessment || {}
  const domains = risk.domains || {}
  const domainData = Object.entries(domains).map(([domain, info]: [string, any]) => ({
    domain,
    score: info.score || 0,
    level: info.level || 'green',
  }))

  const riskColor = getRiskColor(risk.score || 0)

  return (
    <div className="fade-in">
      {/* Breadcrumb */}
      <Link to="/" style={{
        display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
        color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500,
        marginBottom: '1.5rem',
      }}>
        ← Dashboard
      </Link>

      {/* ===== HERO HEADER ===== */}
      <div className="card" style={{
        padding: '2rem',
        marginBottom: '1.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderLeft: `5px solid ${riskColor}`,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <span className="pill" style={{ fontWeight: 700, fontSize: '0.8rem' }}>{code}</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{data.region}</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', marginBottom: '0.5rem' }}>{data.name}</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: 500, lineHeight: 1.5 }}>
            Current fragility assessment based on {domainData.length} monitored domains.
            {risk.score >= 70 && <> <strong style={{ color: 'var(--risk-red)' }}>Immediate attention recommended.</strong></>}
            {risk.score >= 50 && risk.score < 70 && <> Elevated risk — close monitoring advised.</>}
            {risk.score < 50 && <> Within normal operational parameters.</>}
          </p>
        </div>
        <div style={{ textAlign: 'center', minWidth: 120 }}>
          <AlertBadge level={risk.level || 'green'} size="lg" />
        </div>
      </div>

      {/* ===== MAIN GRID ===== */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(280px, 340px) 1fr',
        gap: '1.5rem',
        alignItems: 'start',
      }}>
        {/* LEFT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Fragility Index */}
          <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div className="label" style={{ marginBottom: '1rem' }}>FRAGILITY INDEX</div>
            <RiskGauge score={risk.score || 0} level={risk.level || 'green'} size={170} />
          </div>

          {/* Crisis Forecast */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <div className="label" style={{ marginBottom: '1rem' }}>CRISIS FORECAST</div>
            {['30_days', '60_days', '90_days'].map(period => {
              const prob = risk.crisis_probability?.[period]
              if (!prob) return null
              const val = (prob.probability * 100)
              return (
                <div key={period} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.625rem 0',
                  borderBottom: '1px solid var(--border)',
                  fontSize: '0.875rem',
                }}>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                    {period.replace('_', ' ')}
                  </span>
                  <span style={{
                    fontWeight: 700,
                    color: val > 50 ? 'var(--risk-red)' : val > 25 ? 'var(--risk-orange)' : 'var(--text-primary)',
                  }}>
                    {val.toFixed(1)}%
                  </span>
                </div>
              )
            })}
          </div>

          {/* Key Info */}
          <div className="card card--cream" style={{ padding: '1.5rem' }}>
            <div className="label" style={{ marginBottom: '1rem', color: 'rgba(0,0,0,0.4)' }}>KEY DATA</div>
            <InfoRow label="Population" value={data.population ? `${(data.population / 1e6).toFixed(1)}M` : 'N/A'} />
            <InfoRow label="GDP" value={data.gdp_usd ? `$${(data.gdp_usd / 1e9).toFixed(0)}B` : 'N/A'} />
            <InfoRow label="Capital" value={data.capital || 'N/A'} />
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Domain Breakdown */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div className="label">DOMAIN BREAKDOWN</div>
              <Link to="/regional" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>Compare →</Link>
            </div>
            <DomainChart data={domainData} />
          </div>

          {/* Intelligence Report */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div className="label">INTELLIGENCE REPORT</div>
              <button
                onClick={runAnalysis}
                disabled={analyzing}
                className="btn btn--primary"
                style={{
                  padding: '8px 16px',
                  fontSize: '0.8rem',
                  opacity: analyzing ? 0.6 : 1,
                  cursor: analyzing ? 'wait' : 'pointer',
                }}
              >
                {analyzing ? 'Generating...' : 'Generate Analysis'}
              </button>
            </div>

            {analyzing && (
              <div style={{
                padding: '2rem', textAlign: 'center', color: 'var(--text-muted)',
                background: 'var(--bg-page)', borderRadius: 10,
              }}>
                <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>◎</div>
                Running intelligence analysis...
              </div>
            )}

            {analysis && !analyzing && (
              <div style={{
                background: 'var(--bg-page)',
                padding: '1.5rem',
                borderRadius: 10,
                border: '1px solid var(--border)',
                fontSize: '0.9rem',
                lineHeight: 1.7,
                color: 'var(--text-primary)',
              }}>
                <MarkdownReport content={analysis.report_text} />
              </div>
            )}

            {!analysis && !analyzing && (
              <div style={{
                padding: '3rem 2rem', textAlign: 'center',
                color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.9rem',
              }}>
                Click "Generate Analysis" to create a deep intelligence dossier for this country.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/* ===== HELPERS ===== */

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between',
      padding: '0.5rem 0', borderBottom: '1px solid rgba(0,0,0,0.06)',
      fontSize: '0.875rem',
    }}>
      <span style={{ color: 'rgba(0,0,0,0.5)', fontWeight: 500 }}>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}</span>
    </div>
  )
}

function getRiskColor(score: number): string {
  if (score >= 85) return 'var(--risk-black)'
  if (score >= 70) return 'var(--risk-red)'
  if (score >= 50) return 'var(--risk-orange)'
  if (score >= 30) return 'var(--risk-yellow)'
  return 'var(--risk-green)'
}

function MarkdownReport({ content }: { content: string }) {
  if (!content) return null

  const lines = content.split('\n')
  const elements: JSX.Element[] = []
  let listItems: string[] = []

  function flushList() {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} style={{ paddingLeft: '1.25rem', marginBottom: '1rem' }}>
          {listItems.map((item, j) => (
            <li key={j} style={{ marginBottom: '0.25rem' }}>{formatInline(item)}</li>
          ))}
        </ul>
      )
      listItems = []
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line.startsWith('### ')) {
      flushList()
      elements.push(<h4 key={i} style={{ fontSize: '0.95rem', fontWeight: 700, marginTop: '1.25rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>{line.slice(4)}</h4>)
    } else if (line.startsWith('## ')) {
      flushList()
      elements.push(<h3 key={i} style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>{line.slice(3)}</h3>)
    } else if (line.startsWith('# ')) {
      flushList()
      elements.push(<h2 key={i} style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '1.5rem', marginBottom: '0.75rem' }}>{line.slice(2)}</h2>)
    } else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      listItems.push(line.trim().slice(2))
    } else if (line.trim() === '') {
      flushList()
    } else {
      flushList()
      elements.push(<p key={i} style={{ marginBottom: '0.75rem' }}>{formatInline(line)}</p>)
    }
  }
  flushList()

  return <>{elements}</>
}

function formatInline(text: string): React.ReactNode {
  // Bold
  const parts = text.split(/\*\*(.*?)\*\*/g)
  return parts.map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
  )
}
