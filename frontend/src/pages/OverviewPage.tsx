import { ShieldCheck, Activity, Sun, Globe } from 'lucide-react'

export default function OverviewPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Hero Welcome Panel */}
      <div className="glass-panel" style={{ padding: '28px 32px' }}>
        <div style={{ maxWidth: '800px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 10px', backgroundColor: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '9999px', color: '#38bdf8', fontSize: 'var(--text-xs)', fontWeight: 600, marginBottom: '12px' }}>
            <Activity size={12} aria-hidden="true" />
            <span>Dual-Threat Data Integrity Observatory</span>
          </div>
          <h2 style={{ margin: '0 0 10px', fontSize: 'var(--text-3xl)', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
            AeroTrust Fleet Observatory
          </h2>
          <p style={{ margin: 0, fontSize: 'var(--text-base)', color: '#cbd5e1', lineHeight: '1.6' }}>
            Monitoring the two primary external threats named by Airbus: GNSS jamming/spoofing interference (EASA Top Safety Priority) and intense solar radiation single-event effects.
          </p>
        </div>
      </div>

      {/* KPI & Core Metric Cards (Empty State with calibrated contrast) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>
                GNSS Jamming Cells
              </span>
              <h3 style={{ margin: '8px 0 4px', fontSize: 'var(--text-2xl)', fontWeight: 700, color: '#f8fafc' }}>
                --
              </h3>
            </div>
            <div style={{ padding: '8px', backgroundColor: 'rgba(56, 189, 248, 0.15)', borderRadius: '8px', color: '#38bdf8' }}>
              <Globe size={20} aria-hidden="true" />
            </div>
          </div>
          <p style={{ margin: '12px 0 0', fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
            Awaiting Phase 1 detector ingestion. Coarse H3 res 5.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>
                Fleet Silent Acceptance (SAR)
              </span>
              <h3 style={{ margin: '8px 0 4px', fontSize: 'var(--text-2xl)', fontWeight: 700, color: '#f8fafc' }}>
                --%
              </h3>
            </div>
            <div style={{ padding: '8px', backgroundColor: 'rgba(244, 63, 94, 0.15)', borderRadius: '8px', color: '#f43f5e' }}>
              <ShieldCheck size={20} aria-hidden="true" />
            </div>
          </div>
          <p style={{ margin: '12px 0 0', fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
            Aggregate metric: k-check flags with high NIC/NACp.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>
                Solar Proton Flux (&gt;10 MeV)
              </span>
              <h3 style={{ margin: '8px 0 4px', fontSize: 'var(--text-2xl)', fontWeight: 700, color: '#f8fafc' }}>
                -- pfu
              </h3>
            </div>
            <div style={{ padding: '8px', backgroundColor: 'rgba(251, 191, 36, 0.15)', borderRadius: '8px', color: '#fbbf24' }}>
              <Sun size={20} aria-hidden="true" />
            </div>
          </div>
          <p style={{ margin: '12px 0 0', fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
            Relative exposure index vs altitude &amp; geomagnetic latitude.
          </p>
        </div>
      </div>

      {/* Operational Modules Grid */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: 'var(--text-lg)', fontWeight: 700, color: '#f8fafc' }}>
          System Capabilities &amp; Navigation
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #334155', backgroundColor: 'rgba(15, 23, 42, 0.6)' }}>
            <h4 style={{ margin: '0 0 6px', color: '#38bdf8', fontSize: 'var(--text-sm)', fontWeight: 700 }}>Map &amp; Interference Cells</h4>
            <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>Visualizing regional GNSS jamming and spoofing hot-spots using local vector geography.</p>
          </div>
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #334155', backgroundColor: 'rgba(15, 23, 42, 0.6)' }}>
            <h4 style={{ margin: '0 0 6px', color: '#f43f5e', fontSize: 'var(--text-sm)', fontWeight: 700 }}>Silent Acceptance Rate (SAR)</h4>
            <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>Privacy-preserving aggregate metrics by family x region with Wilson confidence intervals.</p>
          </div>
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #334155', backgroundColor: 'rgba(15, 23, 42, 0.6)' }}>
            <h4 style={{ margin: '0 0 6px', color: '#fbbf24', fontSize: 'var(--text-sm)', fontWeight: 700 }}>Incident Clock</h4>
            <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>Evaluating public Airbus delivery slip impact using published regulatory and AD cases.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

