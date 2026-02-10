import { Alert, AlertLevel } from '../types'
import AlertBadge from './AlertBadge'

interface AlertPanelProps {
  alerts: Alert[]
  title?: string
  maxItems?: number
}

export default function AlertPanel({ alerts, title = 'Active Alerts', maxItems = 10 }: AlertPanelProps) {
  const displayed = alerts.slice(0, maxItems)

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: '8px',
      padding: '1.25rem',
    }}>
      <h3 style={{
        margin: '0 0 1rem 0',
        color: 'var(--text-primary)',
        fontSize: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
      }}>
        {title}
        <span style={{
          background: 'var(--bg-primary)',
          borderRadius: '12px',
          padding: '0.15rem 0.5rem',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
        }}>
          {alerts.length}
        </span>
      </h3>

      {displayed.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No active alerts</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {displayed.map(alert => (
            <div key={alert.id} style={{
              padding: '0.75rem',
              background: 'var(--bg-primary)',
              borderRadius: '6px',
              borderLeft: `3px solid ${getLevelColor(alert.alert_level)}`,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                <AlertBadge level={alert.alert_level} size="sm" />
                <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                  {alert.country_code}
                </span>
              </div>
              <div style={{ color: 'var(--text-primary)', fontSize: '0.85rem', fontWeight: 500 }}>
                {alert.title}
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                {alert.description}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function getLevelColor(level: AlertLevel): string {
  const colors: Record<AlertLevel, string> = {
    green: 'var(--green)',
    yellow: 'var(--yellow)',
    orange: 'var(--orange)',
    red: 'var(--red)',
    black: 'var(--black-alert)',
  }
  return colors[level] || 'var(--text-muted)'
}
