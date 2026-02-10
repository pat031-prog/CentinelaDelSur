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

  if (loading) return <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Cargando dossier...</div>
  if (!data) return <div style={{ padding: '3rem', color: 'var(--risk-red)' }}>Dossier no encontrado</div>

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
        ← Panel Principal
      </Link>

      {/* ===== HERO ===== */}
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
            Evaluación de fragilidad actual basada en {domainData.length} dominios monitoreados.
            {risk.score >= 70 && <> <strong style={{ color: 'var(--risk-red)' }}>Se recomienda atención inmediata.</strong></>}
            {risk.score >= 50 && risk.score < 70 && <> Riesgo elevado — se aconseja monitoreo cercano.</>}
            {risk.score < 50 && <> Dentro de parámetros operativos normales.</>}
          </p>
        </div>
        <div style={{ textAlign: 'center', minWidth: 120 }}>
          <AlertBadge level={risk.level || 'green'} size="lg" />
        </div>
      </div>

      {/* ===== GRID PRINCIPAL ===== */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(280px, 340px) 1fr',
        gap: '1.5rem',
        alignItems: 'start',
      }}>
        {/* COLUMNA IZQUIERDA */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Índice de Fragilidad */}
          <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div className="label" style={{ marginBottom: '1rem' }}>ÍNDICE DE FRAGILIDAD</div>
            <RiskGauge score={risk.score || 0} level={risk.level || 'green'} size={170} />
          </div>

          {/* Pronóstico de Crisis */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <div className="label" style={{ marginBottom: '1rem' }}>PRONÓSTICO DE CRISIS</div>
            {['30_days', '60_days', '90_days'].map(period => {
              const prob = risk.crisis_probability?.[period]
              if (!prob) return null
              const val = (prob.probability * 100)
              const labels: Record<string, string> = {
                '30_days': '30 días',
                '60_days': '60 días',
                '90_days': '90 días',
              }
              return (
                <div key={period} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.625rem 0',
                  borderBottom: '1px solid var(--border)',
                  fontSize: '0.875rem',
                }}>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                    {labels[period] || period}
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

          {/* Datos Clave */}
          <div className="card card--cream" style={{ padding: '1.5rem' }}>
            <div className="label" style={{ marginBottom: '1rem', color: 'rgba(0,0,0,0.4)' }}>DATOS CLAVE</div>
            <InfoRow label="Población" value={data.population ? `${(data.population / 1e6).toFixed(1)}M` : 'N/D'} />
            <InfoRow label="PIB" value={data.gdp_usd ? `$${(data.gdp_usd / 1e9).toFixed(0)}B` : 'N/D'} />
            <InfoRow label="Capital" value={data.capital || 'N/D'} />
          </div>

          {/* Desglose por Dominios */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div className="label">DESGLOSE POR DOMINIO</div>
              <Link to="/regional" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>Comparar →</Link>
            </div>
            <DomainChart data={domainData} />
          </div>
        </div>

        {/* COLUMNA DERECHA: Artículo de Inteligencia */}
        <div className="card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <div className="label" style={{ marginBottom: '0.25rem' }}>ARTÍCULO DE INTELIGENCIA</div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Análisis editorial generado por IA con fuentes en tiempo real
              </span>
            </div>
            <button
              onClick={runAnalysis}
              disabled={analyzing}
              className="btn btn--primary"
              style={{
                padding: '10px 20px',
                fontSize: '0.85rem',
                opacity: analyzing ? 0.6 : 1,
                cursor: analyzing ? 'wait' : 'pointer',
              }}
            >
              {analyzing ? 'Generando...' : 'Generar Artículo'}
            </button>
          </div>

          {analyzing && (
            <div style={{
              padding: '3rem', textAlign: 'center', color: 'var(--text-muted)',
              background: 'var(--bg-page)', borderRadius: 10,
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.75rem', animation: 'pulse 2s infinite' }}>◎</div>
              <p style={{ fontSize: '0.95rem', marginBottom: '0.25rem', fontWeight: 600 }}>Ejecutando análisis de inteligencia...</p>
              <p style={{ fontSize: '0.8rem' }}>Consultando fuentes, procesando datos, redactando artículo</p>
            </div>
          )}

          {analysis && !analyzing && (
            <MagazineArticle content={analysis.report_text} sourcesUsed={analysis.sources_used} />
          )}

          {!analysis && !analyzing && (
            <div style={{
              padding: '4rem 2rem', textAlign: 'center',
              background: 'var(--bg-page)', borderRadius: 10, border: '1px dashed var(--border)',
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.75rem', opacity: 0.3 }}>📰</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: 360, margin: '0 auto', lineHeight: 1.5 }}>
                Haz clic en <strong>"Generar Artículo"</strong> para crear un análisis editorial profundo con fuentes en tiempo real sobre este país.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ===== MAGAZINE ARTICLE RENDERER ===== */

function MagazineArticle({ content, sourcesUsed }: { content: string; sourcesUsed?: boolean }) {
  if (!content) return null

  return (
    <article style={{
      background: 'var(--bg-page)',
      padding: '2rem 2.5rem',
      borderRadius: 12,
      border: '1px solid var(--border)',
      lineHeight: 1.8,
      color: 'var(--text-primary)',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      {sourcesUsed && (
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px',
          background: 'var(--card-sage)', padding: '4px 12px', borderRadius: 100,
          fontSize: '0.7rem', fontWeight: 600, marginBottom: '1.5rem',
          color: 'var(--risk-green)',
        }}>
          ● Fuentes en tiempo real incluidas
        </div>
      )}
      <RenderMarkdown content={content} />
    </article>
  )
}

function RenderMarkdown({ content }: { content: string }) {
  const lines = content.split('\n')
  const elements: JSX.Element[] = []
  let listItems: string[] = []
  let blockquoteLines: string[] = []

  function flushList() {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} style={{
          paddingLeft: '1.25rem', marginBottom: '1.25rem',
          listStyleType: 'disc',
        }}>
          {listItems.map((item, j) => (
            <li key={j} style={{ marginBottom: '0.375rem', fontSize: '0.95rem' }}>{formatInline(item)}</li>
          ))}
        </ul>
      )
      listItems = []
    }
  }

  function flushBlockquote() {
    if (blockquoteLines.length > 0) {
      elements.push(
        <blockquote key={`bq-${elements.length}`} style={{
          borderLeft: '3px solid var(--card-sage)',
          paddingLeft: '1rem',
          margin: '1.25rem 0',
          color: 'var(--text-secondary)',
          fontStyle: 'italic',
          fontSize: '0.95rem',
        }}>
          {blockquoteLines.map((line, j) => (
            <p key={j} style={{ marginBottom: '0.5rem' }}>{formatInline(line)}</p>
          ))}
        </blockquote>
      )
      blockquoteLines = []
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // H1 — Article title
    if (line.startsWith('# ') && !line.startsWith('## ')) {
      flushList()
      flushBlockquote()
      elements.push(
        <h1 key={i} style={{
          fontSize: '1.75rem', fontWeight: 800, lineHeight: 1.15,
          marginBottom: '0.5rem', letterSpacing: '-0.02em',
          color: 'var(--text-primary)',
        }}>{line.slice(2)}</h1>
      )
    }
    // H2 — Section headers
    else if (line.startsWith('## ')) {
      flushList()
      flushBlockquote()
      elements.push(
        <h2 key={i} style={{
          fontSize: '1.25rem', fontWeight: 700, lineHeight: 1.25,
          marginTop: '2rem', marginBottom: '0.75rem',
          color: 'var(--text-primary)',
          paddingBottom: '0.5rem',
          borderBottom: '1px solid var(--border)',
        }}>{line.slice(3)}</h2>
      )
    }
    // H3 — Subsection headers
    else if (line.startsWith('### ')) {
      flushList()
      flushBlockquote()
      elements.push(
        <h3 key={i} style={{
          fontSize: '1.05rem', fontWeight: 700,
          marginTop: '1.5rem', marginBottom: '0.5rem',
          color: 'var(--text-primary)',
        }}>{line.slice(4)}</h3>
      )
    }
    // Metadata line (italic/by line)
    else if (line.startsWith('*') && line.endsWith('*') && !line.startsWith('**')) {
      flushList()
      flushBlockquote()
      elements.push(
        <p key={i} style={{
          fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic',
          marginBottom: '1.5rem', letterSpacing: '0.01em',
          borderBottom: '1px solid var(--border)', paddingBottom: '1rem',
        }}>{line.replace(/^\*|\*$/g, '')}</p>
      )
    }
    // Horizontal rule
    else if (line.trim() === '---' || line.trim() === '***') {
      flushList()
      flushBlockquote()
      elements.push(
        <hr key={i} style={{
          border: 'none', borderTop: '1px solid var(--border)',
          margin: '2rem 0',
        }} />
      )
    }
    // Blockquote
    else if (line.trim().startsWith('> ')) {
      flushList()
      blockquoteLines.push(line.trim().slice(2))
    }
    // List items
    else if (line.trim().startsWith('- ') || line.trim().startsWith('* ') || /^\d+\.\s/.test(line.trim())) {
      flushBlockquote()
      const cleaned = line.trim().replace(/^[-*]\s/, '').replace(/^\d+\.\s/, '')
      listItems.push(cleaned)
    }
    // Empty line
    else if (line.trim() === '') {
      flushList()
      flushBlockquote()
    }
    // Regular paragraph
    else {
      flushList()
      flushBlockquote()
      elements.push(
        <p key={i} style={{
          marginBottom: '1rem', fontSize: '0.95rem', lineHeight: 1.8,
        }}>{formatInline(line)}</p>
      )
    }
  }
  flushList()
  flushBlockquote()

  return <>{elements}</>
}

function formatInline(text: string): React.ReactNode {
  // Handle bold (**text**), links [text](url), and source citations [Fuente: ...]
  const parts: React.ReactNode[] = []
  let remaining = text
  let key = 0

  while (remaining.length > 0) {
    // Check for markdown links [text](url)
    const linkMatch = remaining.match(/\[([^\]]+)\]\(([^)]+)\)/)
    // Check for bold **text**
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/)

    // Find which comes first
    const linkIdx = linkMatch ? remaining.indexOf(linkMatch[0]) : Infinity
    const boldIdx = boldMatch ? remaining.indexOf(boldMatch[0]) : Infinity

    if (linkIdx === Infinity && boldIdx === Infinity) {
      parts.push(remaining)
      break
    }

    if (linkIdx < boldIdx && linkMatch) {
      // Process link
      parts.push(remaining.slice(0, linkIdx))
      parts.push(
        <a key={key++} href={linkMatch[2]} target="_blank" rel="noopener noreferrer" style={{
          color: 'var(--risk-green)', textDecoration: 'underline',
          textDecorationColor: 'rgba(74,124,89,0.3)',
          fontWeight: 500,
        }}>
          {linkMatch[1]} ↗
        </a>
      )
      remaining = remaining.slice(linkIdx + linkMatch[0].length)
    } else if (boldMatch) {
      // Process bold
      parts.push(remaining.slice(0, boldIdx))
      parts.push(<strong key={key++}>{boldMatch[1]}</strong>)
      remaining = remaining.slice(boldIdx + boldMatch[0].length)
    }
  }

  return parts.length === 1 ? parts[0] : <>{parts}</>
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
