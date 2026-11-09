import { Plane, Search, AlertCircle } from 'lucide-react'

export default function FlightDetailPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h2 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
          Flight Detail &amp; Sensor Consistency
        </h2>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
          Inspect single-flight sensor telemetry: Baro vs Geo altitude residuals, kinematic feasibility, and trust scores with explicit abstention reasons.
        </p>

        {/* Flight Selector Input */}
        <div style={{ marginTop: '20px', display: 'flex', gap: '12px', maxWidth: '480px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: '#64748b' }} aria-hidden="true" />
            <input
              type="text"
              placeholder="Search synthetic icao24 (e.g. x0a1b2c)..."
              style={{
                width: '100%',
                padding: '10px 12px 10px 36px',
                backgroundColor: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid #475569',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
              aria-label="Search synthetic flight by icao24"
            />
          </div>
          <button
            style={{
              padding: '10px 18px',
              backgroundColor: '#0369a1',
              color: '#ffffff',
              border: '1px solid #38bdf8',
              borderRadius: '6px',
              fontWeight: 600,
              fontSize: 'var(--text-sm)',
              cursor: 'pointer',
            }}
          >
            Inspect
          </button>
        </div>
      </div>

      {/* Empty State Card */}
      <div className="glass-card" style={{ padding: '48px 32px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', marginBottom: '16px' }}>
          <Plane size={32} aria-hidden="true" />
        </div>
        <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 'var(--text-lg)', fontWeight: 700 }}>
          No Flight Selected
        </h3>
        <p style={{ margin: '0 auto', maxWidth: '460px', color: '#94a3b8', fontSize: 'var(--text-sm)', lineHeight: '1.6' }}>
          Enter an icao24 code above or select an aircraft from the regional map to inspect altitude residuals and detector confidence metrics.
        </p>
        <div style={{ marginTop: '20px', display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'rgba(51, 65, 85, 0.5)', color: '#cbd5e1', fontSize: 'var(--text-xs)' }}>
          <AlertCircle size={14} style={{ color: '#38bdf8' }} aria-hidden="true" />
          <span>Scores become "unknown" when evidence is insufficient (README Section 4.3).</span>
        </div>
      </div>
    </div>
  )
}
