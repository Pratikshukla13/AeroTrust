import { Navigation, Compass } from 'lucide-react'

export default function CorridorsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h2 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
          Delivery Corridor Assessment
        </h2>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
          Corridor-level threat forecasting for aircraft delivery flights departing Toulouse (LFBO) and Hamburg (EDHI).
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', marginBottom: '16px' }}>
          <Compass size={32} aria-hidden="true" />
        </div>
        <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 'var(--text-lg)', fontWeight: 700 }}>
          Delivery Corridors (Stretch Tier)
        </h3>
        <p style={{ margin: '0 auto 16px', maxWidth: '480px', color: '#94a3b8', fontSize: 'var(--text-sm)', lineHeight: '1.6' }}>
          Provides route-specific exposure forecasts across high-risk waypoints before ferry and delivery handovers.
        </p>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'rgba(51, 65, 85, 0.5)', color: '#cbd5e1', fontSize: 'var(--text-xs)' }}>
          <Navigation size={14} style={{ color: '#38bdf8' }} aria-hidden="true" />
          <span>Scheduled for Stretch Tier implementation.</span>
        </div>
      </div>
    </div>
  )
}
