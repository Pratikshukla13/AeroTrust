import { AlertOctagon, Check, FileCode, Shield } from 'lucide-react'

export default function LimitationsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h2 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
          Methodology &amp; Engineering Limitations
        </h2>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
          Frank disclosure of methodological caveats, data boundaries, and outside-in modeling assumptions per README Section 8.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(244, 63, 94, 0.15)', color: '#f43f5e' }}>
              <AlertOctagon size={20} aria-hidden="true" />
            </div>
            <h3 style={{ margin: 0, fontSize: 'var(--text-base)', color: '#f8fafc', fontWeight: 700 }}>
              1. Decision Support, Not Safety-Critical
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#cbd5e1', lineHeight: '1.6' }}>
            AeroTrust is designed for fleet operational visibility and regulatory scoping support. It is not an onboard avionics system and does not issue flight-critical steering guidance.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24' }}>
              <Shield size={20} aria-hidden="true" />
            </div>
            <h3 style={{ margin: 0, fontSize: 'var(--text-base)', color: '#f8fafc', fontWeight: 700 }}>
              2. Relative Radiation Index, Not Probabilities
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#cbd5e1', lineHeight: '1.6' }}>
            The ionizing radiation metric is strictly a <strong>relative exposure index</strong> based on altitude, geomagnetic latitude, and solar proton flux. It never claims a hardware bit-flip failure probability.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <FileCode size={20} aria-hidden="true" />
            </div>
            <h3 style={{ margin: 0, fontSize: 'var(--text-base)', color: '#f8fafc', fontWeight: 700 }}>
              3. Synthetic Injection Validation
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#cbd5e1', lineHeight: '1.6' }}>
            Real-world GNSS spoofing ground truth is confidential. Detector precision and recall are benchmarked via controlled synthetic perturbations (offsets, lateral drifts, and noise) rather than classified operational recordings.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(52, 211, 153, 0.15)', color: '#34d399' }}>
              <Check size={20} aria-hidden="true" />
            </div>
            <h3 style={{ margin: 0, fontSize: 'var(--text-base)', color: '#f8fafc', fontWeight: 700 }}>
              4. External Outside-In Scoping
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#cbd5e1', lineHeight: '1.6' }}>
            Airbus and EASA maintain internal engineering teardowns. AeroTrust operates exclusively on publicly accessible open-source telemetry architectures and validated external reporting.
          </p>
        </div>
      </div>
    </div>
  )
}

