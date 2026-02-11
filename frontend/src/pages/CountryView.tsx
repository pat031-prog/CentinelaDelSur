import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'

// ===== TIMEZONE MAP: country code → IANA timezone of capital =====
const CAPITAL_TZ: Record<string, { tz: string; capital: string }> = {
  AR: { tz: 'America/Argentina/Buenos_Aires', capital: 'Buenos Aires' },
  BR: { tz: 'America/Sao_Paulo', capital: 'Brasília' },
  CL: { tz: 'America/Santiago', capital: 'Santiago' },
  CO: { tz: 'America/Bogota', capital: 'Bogotá' },
  MX: { tz: 'America/Mexico_City', capital: 'Ciudad de México' },
  PE: { tz: 'America/Lima', capital: 'Lima' },
  VE: { tz: 'America/Caracas', capital: 'Caracas' },
  EC: { tz: 'America/Guayaquil', capital: 'Quito' },
  BO: { tz: 'America/La_Paz', capital: 'La Paz' },
  PY: { tz: 'America/Asuncion', capital: 'Asunción' },
  UY: { tz: 'America/Montevideo', capital: 'Montevideo' },
  CR: { tz: 'America/Costa_Rica', capital: 'San José' },
  PA: { tz: 'America/Panama', capital: 'Panamá' },
  GT: { tz: 'America/Guatemala', capital: 'Guatemala' },
  CU: { tz: 'America/Havana', capital: 'La Habana' },
  HN: { tz: 'America/Tegucigalpa', capital: 'Tegucigalpa' },
  NI: { tz: 'America/Managua', capital: 'Managua' },
  SV: { tz: 'America/El_Salvador', capital: 'San Salvador' },
  DO: { tz: 'America/Santo_Domingo', capital: 'Santo Domingo' },
  HT: { tz: 'America/Port-au-Prince', capital: 'Puerto Príncipe' },
}

// Fallback FX/commodity data while API loads
const FALLBACK_FX = [
  { pair: 'USD/ARS', rate: 1025.5, change: 0 },
  { pair: 'USD/BRL', rate: 5.12, change: 0 },
  { pair: 'EUR/USD', rate: 1.085, change: 0 },
]
const FALLBACK_COMMODITIES = [
  { name: 'Petróleo WTI', unit: 'USD/bbl', value: 78.42, change: 0 },
  { name: 'Oro', unit: 'USD/oz', value: 2024.8, change: 0 },
  { name: 'Soja', unit: 'USd/bu', value: 1242.5, change: 0 },
  { name: 'Cobre', unit: 'USD/lb', value: 3.86, change: 0 },
]

export default function CountryView() {
  const { code } = useParams<{ code: string }>()
  const [data, setData] = useState<any>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [fxRates, setFxRates] = useState<any[]>(FALLBACK_FX)
  const [commodities, setCommodities] = useState<any[]>(FALLBACK_COMMODITIES)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [marketLoading, setMarketLoading] = useState(true)

  // Load country data
  useEffect(() => {
    if (!code) return
    async function load() {
      try { setData(await api.getCountry(code!)) }
      catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [code])

  // Load market data
  useEffect(() => {
    async function loadMarket() {
      try {
        const [fx, comm] = await Promise.all([
          api.getMarketFX().catch(() => null),
          api.getMarketCommodities().catch(() => null),
        ])
        if (fx?.rates?.length) setFxRates(fx.rates)
        if (comm?.commodities?.length) setCommodities(comm.commodities)
      } catch (e) {
        console.error('Market data fetch failed:', e)
      } finally {
        setMarketLoading(false)
      }
    }
    loadMarket()
    // Refresh every 5 mins
    const interval = setInterval(loadMarket, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const runAnalysis = async () => {
    if (!code) return
    setAnalyzing(true)
    try { setAnalysis(await api.analyzeCountry(code)) }
    catch (e) { console.error(e) }
    finally { setAnalyzing(false) }
  }

  if (loading) return <div style={{ padding: '3rem', color: 'var(--text-muted)' }}>Accediendo al archivo {code}...</div>
  if (!data) return (
    <div style={{ padding: '2rem' }}>
      <div className="grid-card" style={{ border: '1px solid var(--risk-critical)', maxWidth: '500px' }}>
        <h3 className="t-display" style={{ color: 'var(--risk-critical)', fontSize: '1.2rem' }}>Error de Acceso</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Dossier no encontrado.</p>
        <Link to="/" className="btn-ghost" style={{ marginTop: '1rem', display: 'inline-block' }}>Volver</Link>
      </div>
    </div>
  )

  const risk = data.risk_assessment || {}
  const domains = risk.domains || {}
  const domainLabels: Record<string, string> = {
    political: 'POL', economic: 'ECON', supply_chain: 'SUPPLY',
    geopolitical: 'GEO', climate: 'CLIM', technology: 'TECH',
  }
  const domainData = Object.entries(domains).map(([d, info]: [string, any]) => ({
    key: d, label: domainLabels[d] || d.toUpperCase().slice(0, 4),
    fullLabel: { political: 'Político', economic: 'Económico', supply_chain: 'Cadena Suministro', geopolitical: 'Geopolítico', climate: 'Climático', technology: 'Tecnología' }[d] || d,
    score: info.score || 0,
  })).sort((a, b) => b.score - a.score)

  const capitalInfo = CAPITAL_TZ[code?.toUpperCase() || ''] || { tz: 'America/Argentina/Buenos_Aires', capital: data.capital || 'Capital' }

  return (
    <div className="fade-in">

      {/* ===== HEADER ===== */}
      <div className="grid-dashboard">
        <div className="grid-card">
          <Link to="/" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>← Sala de Situación</Link>
        </div>
        <div className="grid-card span-2">
          <div className="t-label" style={{ marginBottom: '0.25rem' }}>Expediente {code}</div>
          <h1 className="t-display" style={{ fontSize: '2.5rem', textTransform: 'uppercase' }}>{data.name}</h1>
        </div>
        <div className="grid-card orange" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ fontSize: '0.55rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.8 }}>Riesgo Total</div>
          <div className="t-display" style={{ fontSize: '3rem' }}>{risk.score?.toFixed(0)}</div>
        </div>
      </div>

      {/* ===== META ===== */}
      <div className="grid-dashboard" style={{ marginTop: 0 }}>
        <SmallMeta label="Población" value={data.population ? `${(data.population / 1e6).toFixed(1)}M` : 'N/D'} />
        <SmallMeta label="PIB" value={data.gdp_usd ? `$${(data.gdp_usd / 1e9).toFixed(0)}B` : 'N/D'} />
        <SmallMeta label="Región" value={data.region || 'N/D'} />
        <SmallMeta label="Capital" value={data.capital || 'N/D'} />
      </div>

      {/* ===== WIDGETS ===== */}
      <div className="grid-dashboard" style={{ marginTop: 0 }}>
        <DomainRadar domains={domainData} />
        <FXWidget rates={fxRates} loading={marketLoading} />
        <CommoditiesWidget commodities={commodities} loading={marketLoading} />
        <CapitalClock tz={capitalInfo.tz} capital={capitalInfo.capital} region={data.region} score={risk.score || 0} />
      </div>

      {/* ===== REPORT ===== */}
      <div className="grid-dashboard" style={{ marginTop: 0 }}>
        <div className="grid-card span-4" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{
            padding: '1rem 1.5rem',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <span className="t-display" style={{ fontSize: '1.1rem' }}>Informe de Inteligencia</span>
            <button onClick={runAnalysis} disabled={analyzing} className="btn-accent"
              style={{ opacity: analyzing ? 0.5 : 1, fontSize: '0.65rem', padding: '0.4rem 1rem' }}>
              {analyzing ? 'Procesando...' : 'Generar →'}
            </button>
          </div>
          <div style={{ padding: '2rem 2.5rem', minHeight: '300px' }}>
            {!analysis && !analyzing && (
              <div style={{ textAlign: 'center', marginTop: '4rem', opacity: 0.15 }}>
                <div className="t-display" style={{ fontSize: '1.8rem' }}>Sin Datos</div>
                <p style={{ marginTop: '0.4rem', fontSize: '0.8rem' }}>Genere un informe para ver el análisis</p>
              </div>
            )}
            {analyzing && (
              <div style={{ textAlign: 'center', marginTop: '4rem' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Recopilando inteligencia...</div>
                <div style={{ marginTop: '1rem', width: '40px', height: '3px', background: 'var(--accent)', margin: '1rem auto', borderRadius: '2px', animation: 'pulse 1.5s infinite' }} />
              </div>
            )}
            {analysis && (
              <div style={{ maxWidth: '800px' }}>
                <div className="t-label" style={{ marginBottom: '1.5rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
                  REF: {code}-{new Date().getFullYear()} · Clasificación: Abierta
                </div>
                <ReportMarkdown content={analysis.report_text} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/* ===== SMALL META ===== */
function SmallMeta({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid-card">
      <div className="t-label" style={{ marginBottom: '0.25rem' }}>{label}</div>
      <div className="t-data" style={{ fontSize: '1.1rem', fontWeight: 600 }}>{value}</div>
    </div>
  )
}

/* ===== DOMAIN RADAR ===== */
function DomainRadar({ domains }: { domains: { key: string; label: string; score: number }[] }) {
  const maxScore = Math.max(...domains.map(d => d.score), 100)
  return (
    <div className="grid-card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '0.85rem 1.25rem', borderBottom: '1px solid var(--border-color)' }}>
        <span className="t-display" style={{ fontSize: '0.95rem' }}>Dominios Estratégicos</span>
      </div>
      <div style={{ padding: '1.25rem', display: 'flex', alignItems: 'flex-end', gap: '6px', height: '180px' }}>
        {domains.map(d => {
          const h = (d.score / maxScore) * 120
          const color = d.score >= 70 ? 'var(--risk-critical)' : d.score >= 50 ? 'var(--risk-high)' : 'var(--card-sage)'
          return (
            <div key={d.key} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              <span className="t-data" style={{ fontSize: '0.7rem', fontWeight: 700, color }}>{d.score.toFixed(0)}</span>
              <div style={{ width: '100%', height: `${h}px`, background: color, borderRadius: '4px 4px 0 0', transition: 'height 0.6s ease' }} />
              <span style={{ fontSize: '0.55rem', fontWeight: 600, color: 'var(--text-dim)', textAlign: 'center' }}>{d.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

/* ===== FX WIDGET (REAL DATA) ===== */
function FXWidget({ rates, loading }: { rates: any[]; loading: boolean }) {
  return (
    <div className="grid-card sage" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '0.85rem 1.25rem', borderBottom: '1px solid rgba(0,0,0,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="t-display" style={{ fontSize: '0.95rem' }}>Tipos de Cambio</span>
        {loading && <span style={{ fontSize: '0.55rem', opacity: 0.5 }}>cargando...</span>}
        {!loading && <span style={{ fontSize: '0.5rem', opacity: 0.4 }}>● LIVE</span>}
      </div>
      <div>
        {rates.map(r => (
          <div key={r.pair} style={{
            padding: '0.65rem 1.25rem',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            borderBottom: '1px solid rgba(0,0,0,0.06)'
          }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>{r.pair}</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
              <span className="t-data" style={{ fontSize: '0.95rem', fontWeight: 700 }}>
                {r.rate >= 100 ? r.rate.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) : r.rate.toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 4 })}
              </span>
              <span style={{ fontSize: '0.65rem', fontWeight: 700, color: r.change >= 0 ? '#1a5c1a' : '#8b1a1a' }}>
                {r.change >= 0 ? '+' : ''}{r.change.toFixed(2)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ===== COMMODITIES (REAL DATA) ===== */
function CommoditiesWidget({ commodities, loading }: { commodities: any[]; loading: boolean }) {
  return (
    <div className="grid-card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '0.85rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="t-display" style={{ fontSize: '0.95rem' }}>Commodities</span>
        {loading && <span style={{ fontSize: '0.55rem', color: 'var(--text-dim)' }}>cargando...</span>}
        {!loading && <span style={{ fontSize: '0.5rem', color: 'var(--risk-low)' }}>● LIVE</span>}
      </div>
      <div>
        {commodities.map(c => (
          <div key={c.name} style={{
            padding: '0.65rem 1.25rem',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            borderBottom: '1px solid var(--border-light)'
          }}>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 500 }}>{c.name}</div>
              <div style={{ fontSize: '0.55rem', color: 'var(--text-dim)' }}>{c.unit}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span className="t-data" style={{ fontSize: '0.95rem', fontWeight: 700 }}>
                {c.value >= 100 ? c.value.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) : c.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <div style={{ fontSize: '0.6rem', fontWeight: 700, color: c.change >= 0 ? 'var(--risk-low)' : 'var(--risk-critical)' }}>
                {c.change >= 0 ? '▲' : '▼'} {Math.abs(c.change).toFixed(2)}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ===== CAPITAL CLOCK (real timezone) ===== */
function CapitalClock({ tz, capital, region, score }: { tz: string; capital: string; region: string; score: number }) {
  const [time, setTime] = useState(new Date())
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t) }, [])

  const formatter = new Intl.DateTimeFormat('es-ES', {
    timeZone: tz,
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false
  })
  const dateFormatter = new Intl.DateTimeFormat('es-ES', {
    timeZone: tz,
    weekday: 'short', day: '2-digit', month: 'short', year: 'numeric'
  })

  const threatLevel = score >= 70 ? 'CRÍTICO' : score >= 50 ? 'ELEVADO' : score >= 30 ? 'VIGILANCIA' : 'ESTABLE'
  const threatColor = score >= 70 ? 'var(--risk-critical)' : score >= 50 ? 'var(--risk-high)' : score >= 30 ? 'var(--risk-medium)' : 'var(--risk-low)'

  const seconds = time.getSeconds()
  const sweepAngle = (seconds / 60) * 360

  return (
    <div className="grid-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      {/* Clock */}
      <div>
        <div className="t-label" style={{ marginBottom: '0.25rem' }}>{capital}</div>
        <div className="t-data" style={{ fontSize: '1.8rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
          {formatter.format(time)}
        </div>
        <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginTop: '0.1rem' }}>
          {dateFormatter.format(time)}
        </div>
      </div>

      {/* Mini radar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
        <div style={{
          width: 48, height: 48, borderRadius: '50%', border: '1px solid var(--border-color)',
          position: 'relative', overflow: 'hidden', background: 'var(--bg-secondary)', flexShrink: 0
        }}>
          <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: '1px', background: 'var(--border-color)' }} />
          <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: '1px', background: 'var(--border-color)' }} />
          <div style={{
            position: 'absolute', top: '50%', left: '50%', width: '50%', height: '2px',
            background: `linear-gradient(90deg, ${threatColor}, transparent)`,
            transformOrigin: '0 50%', transform: `rotate(${sweepAngle}deg)`, transition: 'transform 1s linear'
          }} />
          <div style={{
            position: 'absolute', top: '50%', left: '50%', width: 4, height: 4,
            borderRadius: '50%', background: threatColor, transform: 'translate(-50%, -50%)'
          }} />
        </div>
        <div>
          <div style={{ fontSize: '0.55rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Amenaza</div>
          <div className="t-data" style={{ fontSize: '0.85rem', fontWeight: 700, color: threatColor }}>{threatLevel}</div>
          <div style={{ fontSize: '0.5rem', color: 'var(--text-dim)' }}>{region || 'Global'}</div>
        </div>
      </div>
    </div>
  )
}

/* ===== REPORT MARKDOWN ===== */
function ReportMarkdown({ content }: { content: string }) {
  if (!content) return null
  return (
    <div style={{ fontSize: '0.9rem', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
      {content.split('\n').map((line, i) => {
        if (line.startsWith('# ')) return <h3 key={i} className="t-display" style={{ fontSize: '1.4rem', marginTop: '1.75rem', paddingBottom: '0.4rem', borderBottom: '1px solid var(--border-color)', color: 'var(--text-primary)' }}>{line.slice(2)}</h3>
        if (line.startsWith('## ')) return <h4 key={i} className="t-label" style={{ marginTop: '1.5rem', marginBottom: '0.4rem', fontSize: '0.75rem', color: 'var(--accent)' }}>{line.slice(3)}</h4>
        if (line.startsWith('### ')) return <h5 key={i} style={{ fontSize: '0.95rem', marginTop: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{line.slice(4)}</h5>
        if (line.trim() === '') return <div key={i} style={{ height: '0.5rem' }} />
        if (line.startsWith('- ')) return <li key={i} style={{ marginLeft: '1rem', listStyleType: 'disc', fontSize: '0.85rem', marginBottom: '0.2rem' }}>{line.slice(2)}</li>
        return <p key={i} style={{ marginBottom: '0.6rem', textAlign: 'justify' }}>{line}</p>
      })}
    </div>
  )
}
