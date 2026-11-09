import { ShieldAlert, Info, Lock } from 'lucide-react'

export default function SARPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
              Silent Acceptance Rate (SAR)
            </h2>
            <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
              Proportion of flights where at least <em>k</em> independent spoofing checks flagged inconsistency while ADS-B integrity flags (NIC/NACp) remained high throughout.
            </p>
          </div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'rgba(52, 211, 153, 0.1)', border: '1px solid rgba(52, 211, 153, 0.3)', color: '#34d399', fontSize: 'var(--text-xs)', fontWeight: 600 }}>
            <Lock size={12} aria-hidden="true" />
            <span>Differential Privacy Guardrail Active</span>
          </div>
        </div>

        {/* Guardrail Rules Disclosure */}
        <div style={{ marginTop: '16px', padding: '12px 16px', borderRadius: '8px', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <Info size={16} style={{ color: '#38bdf8', flexShrink: 0 }} aria-hidden="true" />
          <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1', lineHeight: '1.5' }}>
            <strong>Privacy Policy (README Section 4.4):</strong> Aggregated by aircraft family &times; region &times; month only. Any cell with fewer than 30 flagged flights is automatically suppressed. Individual tail numbers and icao24 codes are never stored in SAR records.
          </p>
        </div>
      </div>

      {/* Aggregate Table Empty State */}
      <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', marginBottom: '16px' }}>
          <ShieldAlert size={32} aria-hidden="true" />
        </div>
        <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 'var(--text-lg)', fontWeight: 700 }}>
          SAR Aggregations Pending Pipeline Execution
        </h3>
        <p style={{ margin: '0 auto 20px', maxWidth: '520px', color: '#94a3b8', fontSize: 'var(--text-sm)', lineHeight: '1.6' }}>
          Once the Phase 4 validation pipeline executes, regional SAR values and Wilson score confidence intervals will be tabulated here for A320-family, A330, and A350 cohorts.
        </p>

        <div style={{ display: 'inline-grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', textAlign: 'left', maxWidth: '600px', width: '100%', margin: '0 auto' }}>
          <div style={{ padding: '12px', borderRadius: '6px', backgroundColor: '#1e293b', border: '1px solid #334155' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>A320-family Target</span>
            <div style={{ fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>Suppression &ge; 30</div>
          </div>
          <div style={{ padding: '12px', borderRadius: '6px', backgroundColor: '#1e293b', border: '1px solid #334155' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>A330 Target</span>
            <div style={{ fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>Suppression &ge; 30</div>
          </div>
          <div style={{ padding: '12px', borderRadius: '6px', backgroundColor: '#1e293b', border: '1px solid #334155' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>A350 Target</span>
            <div style={{ fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>Suppression &ge; 30</div>
          </div>
        </div>
      </div>
    </div>
  )
}

