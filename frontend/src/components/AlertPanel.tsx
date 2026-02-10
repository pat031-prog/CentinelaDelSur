import { Alert, AlertLevel } from '../types'
import AlertBadge from './AlertBadge'

interface AlertPanelProps {
  alerts: Alert[]
  title?: string
  maxItems?: number
}

export default function AlertPanel({ alerts, title = 'LIVE INTEL FEED', maxItems = 10 }: AlertPanelProps) {
  const displayed = alerts.slice(0, maxItems)

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'white',
      borderRadius: '16px',
      border: '1px solid var(--border)',
      overflow: 'hidden' // Important for rounded corners
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem 1.25rem',
        borderBottom: '1px solid var(--border)',
        background: '#f8fafc',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <h3 style={{
          margin: 0,
          color: 'var(--text-secondary)',
          fontSize: '0.8rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span style={{
            display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%',
            background: 'var(--risk-high)',
            animation: 'pulse 2s infinite'
          }} />
          {title}
        </h3>
        <span style={{
          fontFamily: 'JetBrains Mono',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
          background: '#e2e8f0',
          padding: '2px 8px',
          borderRadius: '12px',
          fontWeight: 600
        }}>
          {alerts.length}
        </span>
      </div>

      {/* List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '0',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {displayed.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '3rem 2rem', color: 'var(--text-secondary)', fontSize: '0.85rem'
          }}>
            No active signals.
          </div>
        ) : (
          displayed.map((alert, index) => (
            <div key={alert.id} style={{
              padding: '1rem 1.25rem',
              borderBottom: '1px solid #f1f5f9',
              transition: 'background 0.2s',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.25rem'
            }}
              onMouseEnter={e => e.currentTarget.style.background = '#f8fafc'}
              onMouseLeave={e => e.currentTarget.style.background = 'white'}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{
                  fontFamily: 'JetBrains Mono',
                  fontSize: '0.7rem',
                  color: 'var(--text-secondary)',
                  fontWeight: 600
                }}>
                  {alert.country_code}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{new Date(alert.created_at).toLocaleDateString()}</span>
              </div>

              <div style={{
                color: 'var(--text-primary)',
                fontSize: '0.9rem',
                fontWeight: 600,
                lineHeight: '1.4'
              }}>
                {alert.title}
              </div>

              <div style={{
                color: 'var(--text-secondary)',
                fontSize: '0.8rem',
                lineHeight: '1.4',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}>
                {alert.description}
              </div>

              <div style={{ marginTop: '0.5rem' }}>
                <AlertBadge level={alert.alert_level} size="sm" showLabel={true} pulsing={false} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
