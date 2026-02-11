import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import RiskGauge from '../components/RiskGauge'
// Removed DomainChart import as we will do simple bars for now or refactor it later.
// For now, let's implement a brutalist list for domains.

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

  if (loading) return <div className="type-mono" style={{ padding: '2rem' }}>ACCEDIENDO AL ARCHIVO {code}...</div>

  if (!data) return (
    <div style={{ padding: '2rem', border: '1px solid var(--risk-critical)', color: 'var(--risk-critical)' }}>
      <h3 className="type-mono">ERROR DE ACCESO</h3>
      <p>DOSSIER NO ENCONTRADO O RESTRINGIDO</p>
      <Link to="/" className="btn-brutalist" style={{ marginTop: '1rem', display: 'inline-block' }}>VOLVER</Link>
    </div>
  )

  const risk = data.risk_assessment || {}
  const domains = risk.domains || {}
  const domainData = Object.entries(domains).map(([domain, info]: [string, any]) => ({
    domain,
    score: info.score || 0,
    level: info.level || 'green',
  }))

  return (
    <div className="fade-in" style={{ maxWidth: '1400px', margin: '0 auto' }}>

      {/* ===== DOSSIER HEADER ===== */}
      <div className="brutalist-grid" style={{ marginBottom: '2rem' }}>
        <div className="grid-cell">
          <Link to="/" className="type-mono" style={{ fontSize: '0.8rem', textDecoration: 'underline' }}>
            &larr; SALA DE SITUACIÓN
          </Link>
        </div>
        <div className="grid-cell double-width" style={{ borderLeft: 'var(--border-width) solid var(--border-color)' }}>
          <div className="type-mono" style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>EXPEDIENTE {code}</div>
          <h1 className="type-display text-xl" style={{ textTransform: 'uppercase' }}>{data.name}</h1>
        </div>
        <div className="grid-cell" style={{ borderLeft: 'var(--border-width) solid var(--border-color)', textAlign: 'center', background: '#000', color: '#FFF' }}>
          <div className="type-mono" style={{ fontSize: '0.8rem', opacity: 0.8 }}>RIESGO TOTAL</div>
          <div className="type-display text-xl">{risk.score?.toFixed(0)}</div>
        </div>
      </div>

      {/* ===== METADATA GRID ===== */}
      <div className="brutalist-grid" style={{ marginBottom: '4rem' }}>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>POBLACIÓN</div>
          <div className="type-display text-md">{data.population ? `${(data.population / 1e6).toFixed(1)}M` : 'N/D'}</div>
        </div>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>PIB (USD)</div>
          <div className="type-display text-md">{data.gdp_usd ? `$${(data.gdp_usd / 1e9).toFixed(0)}B` : 'N/D'}</div>
        </div>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>REGIÓN</div>
          <div className="type-display text-md">{data.region}</div>
        </div>
        <div className="grid-cell">
          <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666' }}>CAPITAL</div>
          <div className="type-display text-md">{data.capital || 'N/D'}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '0' }}>

        {/* LEFT COL: VULNERABILITY */}
        <div style={{ border: 'var(--border-width) solid var(--border-color)', borderRight: 'none' }}>
          <div style={{ padding: '1rem', borderBottom: 'var(--border-width) solid var(--border-color)', background: '#EAEAEA' }}>
            <h3 className="type-mono">DOMINIOS ESTRATÉGICOS</h3>
          </div>
          {domainData.map(d => (
            <div key={d.domain} style={{ padding: '1rem', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="type-mono" style={{ fontSize: '0.8rem' }}>{d.domain}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '100px', height: '8px', border: '1px solid #000', padding: '1px' }}>
                  <div style={{ width: `${d.score}%`, height: '100%', background: '#000' }}></div>
                </div>
                <span className="type-mono" style={{ fontWeight: 700 }}>{d.score.toFixed(0)}</span>
              </div>
            </div>
          ))}
        </div>

        {/* RIGHT COL: INTELLIGENCE REPORT */}
        <div style={{ border: 'var(--border-width) solid var(--border-color)' }}>
          <div style={{
            padding: '1rem',
            borderBottom: 'var(--border-width) solid var(--border-color)',
            background: '#EAEAEA',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <h3 className="type-mono">INFORME DE INTELIGENCIA</h3>
            <button
              onClick={runAnalysis}
              disabled={analyzing}
              className="type-mono"
              style={{
                background: analyzing ? '#ccc' : '#000',
                color: '#fff',
                padding: '4px 12px',
                fontSize: '0.8rem'
              }}
            >
              {analyzing ? '/// PROCESANDO ///' : 'GENERAR NUEVO'}
            </button>
          </div>

          <div style={{ padding: '3rem', minHeight: '400px', background: '#FFF' }}>
            {!analysis && !analyzing && (
              <div style={{ textAlign: 'center', opacity: 0.3, marginTop: '4rem' }}>
                <div className="type-display text-xl">SIN DATOS</div>
              </div>
            )}

            {analyzing && (
              <div style={{ textAlign: 'center', marginTop: '4rem' }}>
                <div className="type-mono">RECOPILANDO INTELIGENCIA WEB...</div>
              </div>
            )}

            {analysis && (
              <article className="prose">
                <div className="type-mono" style={{ fontSize: '0.7rem', color: '#666', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid #eee' }}>
                  REF: {code}-{new Date().getFullYear()} // CLASIFICACIÓN: ABIERTA
                </div>
                <RenderMarkdown content={analysis.report_text} />
              </article>
            )}
          </div>
        </div>

      </div>

    </div>
  )
}

function RenderMarkdown({ content }: { content: string }) {
  if (!content) return null

  return (
    <div style={{ fontFamily: 'var(--font-display)', lineHeight: 1.6, fontSize: '1.1rem' }}>
      {content.split('\n').map((line, i) => {
        if (line.startsWith('# ')) return <h3 key={i} className="type-display" style={{ fontSize: '1.8rem', marginTop: '2rem', borderBottom: '2px solid black', paddingBottom: '0.5rem' }}>{line.slice(2)}</h3>
        if (line.startsWith('## ')) return <h4 key={i} className="type-mono" style={{ fontSize: '1rem', marginTop: '1.5rem', fontWeight: 700 }}>{line.slice(3)}</h4>
        if (line.startsWith('### ')) return <h5 key={i} style={{ fontSize: '1.1rem', marginTop: '1rem', fontWeight: 700 }}>{line.slice(4)}</h5>
        if (line.trim() === '') return <div key={i} style={{ height: '1rem' }} />
        if (line.startsWith('- ')) return <li key={i} style={{ marginLeft: '1rem', listStyle: 'square', fontFamily: 'var(--font-body)', fontSize: '1rem' }}>{line.slice(2)}</li>

        return <p key={i} style={{ marginBottom: '0.8rem', textAlign: 'justify', fontFamily: 'var(--font-body)', fontSize: '1rem' }}>{line}</p>
      })}
    </div>
  )
}
