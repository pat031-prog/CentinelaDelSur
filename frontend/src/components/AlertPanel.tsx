import { Alert, AlertLevel } from '../types'
import AlertBadge from './AlertBadge'

interface AlertPanelProps {
  alerts: Alert[]
  title?: string
  maxItems?: number
}

const LEVEL_COLORS: Record<AlertLevel, string> = {
  green: 'var(--green)',
  yellow: 'var(--yellow)',
  orange: 'var(--orange)',
  red: 'var(--red)',
  black: 'var(--black-alert)',
}

export default function AlertPanel({ alerts, title = 'LIVE INTEL FEED', maxItems = 10 }: AlertPanelProps) {
  const displayed = alerts.slice(0, maxItems)

  return (
    <div className="glass-panel" style={{
      height: '100%',
      borderRadius: '8px',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Sticky Header */}
      <div style={{
        padding: '1rem 1.25rem',
        borderBottom: '1px solid var(--border)',
        background: 'rgba(5, 9, 16, 0.6)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <h3 style={{
          margin: 0,
          color: 'var(--text-secondary)',
          fontSize: '0.85rem',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <span style={{
            display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%',
            background: 'var(--red)', boxShadow: '0 0 6px var(--red)',
            animation: 'blink 1.5s infinite'
          }} />
          {title}
        </h3>
        <span style={{
          fontFamily: 'JetBrains Mono',
          fontSize: '0.75rem',
          color: 'var(--accent)',
          background: 'var(--accent-glow)',
          padding: '2px 6px',
          borderRadius: '4px'
        }}>
          {alerts.length}
        </span>
      </div>

      {/* Scrollable List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem'
      }}>
        {displayed.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.85rem',
            fontFamily: 'JetBrains Mono'
          }}>
            NO ACTIVE SIGNALS DETECTED
          </div>
        ) : (
          displayed.map((alert, index) => {
            const color = LEVEL_COLORS[alert.alert_level] || 'var(--text-muted)'
            return (
              <div key={alert.id} className="animate-fade-in-up" style={{
                animationDelay: `${index * 50}ms`,
                padding: '0.85rem',
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: '6px',
                border: '1px solid transparent',
                borderLeft: `3px solid ${color}`,
                transition: 'all 0.2s ease',
                cursor: 'pointer'
              }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)'
                  e.currentTarget.style.transform = 'translateX(4px)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'
                  e.currentTarget.style.transform = 'none'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{
                    fontFamily: 'JetBrains Mono',
                    fontSize: '0.7rem',
                    color: 'var(--text-muted)'
                  }}>
                    {alert.country_code} • {new Date(alert.created_at).toLocaleDateString()}
                  </span>
                  <AlertBadge level={alert.alert_level} size="sm" showLabel={true} pulsing={false} />
                </div>

                <div style={{
                  color: 'var(--text-primary)',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  marginBottom: '0.25rem',
                  lineHeight: '1.4'
                }}>
                  {alert.title}
                </div>

                <div style={{
                  color: 'var(--text-secondary)',
                  fontSize: '0.75rem',
                  lineHeight: '1.4',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {alert.description}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
