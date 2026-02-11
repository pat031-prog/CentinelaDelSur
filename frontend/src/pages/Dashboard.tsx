import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Country, Alert } from '../types'
import GeopoliticsRadar from '../components/GeopoliticsRadar'
import CommodityTicker from '../components/CommodityTicker'
import TechSingularityPanel from '../components/TechSingularityPanel'
import { Activity, Globe, AlertTriangle, ShieldAlert } from 'lucide-react'

import BootSequence from '../components/BootSequence'

export default function Dashboard() {
  const [countries, setCountries] = useState<Country[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [booting, setBooting] = useState(true) // New Boot State

  // War Room Focus State
  const [selectedCode, setSelectedCode] = useState<string>('ARG') // Default to ARG
  const [deepData, setDeepData] = useState<any>(null)
  const [scanning, setScanning] = useState(false)

  // Initial Load
  useEffect(() => {
    async function load() {
      try {
        const [c, a] = await Promise.all([api.getCountries(), api.getAlerts()])
        setCountries(c || [])
        setAlerts(a?.alerts || [])
        if (c && c.length > 0) {
          // Find most critical or default to ARG
          const critical = c.find((x: Country) => x.current_risk_score >= 70)
          setSelectedCode(critical ? critical.code : 'ARG')
        }
      } catch (e) {
        console.error("Dashboard load failed:", e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Deep Scan on Selection
  useEffect(() => {
    if (!selectedCode) return

    async function scan() {
      setScanning(true)
      setDeepData(null)
      try {
        // Parallel fetch for speed: standard data + deep analysis
        // Note: In a real scenario, we might want to trigger deep analysis only on demand 
        // to save tokens, but for the "War Room" feel, we do it automatically.
        const data = await api.analyzeCountry(selectedCode, 'deep')
        setDeepData(data)
      } catch (e) {
        console.error("Deep scan failed:", e)
      } finally {
        setScanning(false)
      }
    }
    scan()
  }, [selectedCode])

  // RENDER BOOT SEQUENCE
  if (booting) return <BootSequence onComplete={() => setBooting(false)} />

  if (loading) return null // Should be handled by boot sequence or just hidden behind it

  const selectedCountry = countries.find(c => c.code === selectedCode)
  const avgRisk = countries.length ? countries.reduce((a, c) => a + c.current_risk_score, 0) / countries.length : 0

  return (
    <div className="fade-in" style={{ minHeight: '100vh', position: 'relative' }}>
      {/* CRT Overlay Effect */}
      <div className="crt-overlay" style={{ position: 'fixed', inset: 0, zIndex: 50 }} />

      {/* Background Particles (CSS only for now) */}
      <div style={{ position: 'fixed', inset: 0, zIndex: -1, background: 'radial-gradient(circle at 50% 50%, #1a1f35 0%, #0a0f1e 100%)' }} />

      {/* ===== TOP BAR (ZONE 1) ===== */}
      <header className="glass-panel" style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '1rem 2rem', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}>
        <div>
          <div className="t-label neon-text" style={{ fontSize: '0.7rem' }}>SISTEMA DE VIGILANCIA HEMISFÉRICA</div>
          <h1 className="t-display t-lg" style={{ margin: 0, textShadow: '0 0 10px rgba(255,255,255,0.1)' }}>ATALAYA <span style={{ color: 'var(--accent)' }}>WAR ROOM</span></h1>
        </div>
        <div style={{ display: 'flex', gap: '2rem' }}>
          <MetricWidget label="ENTIDADES" value={countries.length} />
          <MetricWidget label="RIESGO REGIONAL" value={avgRisk.toFixed(1)} color={avgRisk > 50 ? 'red' : 'blue'} />
          <MetricWidget label="ALERTA DEFCON" value="4" color="orange" />
        </div>
      </header>

      {/* ===== MAIN GRID ===== */}
      <div className="grid-dashboard-organic">

        {/* ZONE 2: NAVIGATION / RISK MATRIX (LEFT) */}
        <div className="zone-left glass-panel" style={{ height: 'calc(100vh - 180px)', overflowY: 'auto' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <div className="t-label">ESTACIONES</div>
          </div>
          {countries.sort((a, b) => b.current_risk_score - a.current_risk_score).map(c => (
            <div key={c.code}
              onClick={() => setSelectedCode(c.code)}
              style={{
                padding: '0.75rem 1rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                background: selectedCode === c.code ? 'rgba(0, 170, 255, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                borderLeft: selectedCode === c.code ? '3px solid var(--accent)' : '3px solid transparent',
                cursor: 'pointer',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                transition: 'all 0.2s ease-in-out',
                boxShadow: selectedCode === c.code ? '0 0 15px rgba(0, 170, 255, 0.2)' : 'none'
              }}
              className="hover-bg"
            >
              <div>
                <div style={{
                  fontWeight: 700,
                  fontSize: '0.9rem',
                  color: selectedCode === c.code ? '#fff' : 'var(--text-primary)',
                  textShadow: selectedCode === c.code ? '0 0 8px rgba(255,255,255,0.5)' : 'none'
                }}>{c.name}</div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6, letterSpacing: '0.05em' }}>{c.code}</div>
              </div>
              <div style={{
                fontWeight: 700,
                color: c.current_risk_score >= 70 ? 'var(--risk-critical)' : 'var(--text-secondary)',
                textShadow: c.current_risk_score >= 70 ? '0 0 10px red' : 'none'
              }}>
                {c.current_risk_score.toFixed(0)}
              </div>
            </div>
          ))}
        </div>

        {/* ZONE 3: FOCUS / DEEP ANALYSIS (CENTER) */}
        <div className="zone-center" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

          {/* 3.1: COMMODITY TICKER */}
          {deepData?.key_commodities && (
            <CommodityTicker commodities={deepData.key_commodities} />
          )}

          {/* 3.2: MAIN ANALYSIS PANEL */}
          <div className="glass-panel" style={{ flex: 1, padding: '2rem', position: 'relative' }}>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <div>
                <div className="t-label" style={{ color: 'var(--accent)' }}>OBJETIVO ACTIVO</div>
                <h2 className="t-display t-xl">{selectedCountry?.name.toUpperCase()}</h2>
              </div>
              {scanning && <div className="pulse-critical t-label" style={{ color: 'var(--accent)' }}>ESCANEANDO VECTORES...</div>}
            </div>

            {/* Content Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

              {/* LEFT COL: RADAR & TECH */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {deepData?.alignment_score ? (
                  <GeopoliticsRadar
                    score={deepData.alignment_score.usa_china_axis}
                    description={deepData.alignment_score.description}
                  />
                ) : (
                  <div className="glass-panel" style={{ height: '140px', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5 }}>
                    {scanning ? "Sincronizando satélites..." : "Sin datos de alineación."}
                  </div>
                )}

                {deepData?.tech_biotech_radar ? (
                  <TechSingularityPanel data={deepData.tech_biotech_radar} />
                ) : null}
              </div>

              {/* RIGHT COL: SYNTHESIS */}
              <div>
                <div className="t-label" style={{ marginBottom: '0.5rem' }}>RESUMEN EJECUTIVO</div>
                <div style={{
                  fontSize: '0.9rem', lineHeight: 1.6,
                  height: '300px', overflowY: 'auto',
                  paddingRight: '0.5rem'
                }}>
                  {deepData?.executive_summary || (scanning ? "Esperando enlace de datos..." : "Selecciona una entidad para iniciar análisis profundo.")}
                </div>

                {deepData?.supply_chain_alert && (
                  <div style={{ marginTop: '1.5rem', padding: '1rem', border: '1px solid var(--risk-critical)', background: 'rgba(255, 68, 68, 0.05)' }}>
                    <div className="t-label" style={{ color: 'var(--risk-critical)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <AlertTriangle size={14} /> ALERTA DE SUMINISTRO
                    </div>
                    <div style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                      {deepData.supply_chain_alert}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ZONE 4: MICRO-ALERTS (RIGHT) */}
        <div className="zone-right glass-panel" style={{ height: 'calc(100vh - 180px)', overflowY: 'auto' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <div className="t-label">MICRO-ALERTAS</div>
          </div>
          {alerts.map(a => (
            <div key={a.id} style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.6rem', fontWeight: 700, padding: '1px 4px', background: 'var(--bg-secondary)', borderRadius: '2px' }}>{a.country_code}</span>
                <span style={{ fontSize: '0.6rem', opacity: 0.5 }}>{new Date(a.created_at).toLocaleTimeString()}</span>
              </div>
              <div style={{ fontSize: '0.8rem', lineHeight: 1.3 }}>{a.title}</div>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}

function MetricWidget({ label, value, color }: { label: string, value: string | number, color?: string }) {
  return (
    <div>
      <div className="t-label" style={{ marginBottom: '0.2rem' }}>{label}</div>
      <div className="t-display" style={{ fontSize: '1.5rem', color: color === 'red' ? 'var(--risk-critical)' : color === 'orange' ? 'var(--risk-high)' : color === 'blue' ? 'var(--accent)' : 'inherit' }}>
        {value}
      </div>
    </div>
  )
}
