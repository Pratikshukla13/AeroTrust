import { EyeOff, Lock, AlertTriangle } from 'lucide-react'

export default function WatchlistPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
              Precursor Watchlist (Internal / Private)
            </h2>
            <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
              Hypothesis generator scanning A320-family cruise telemetry for sharp pitch-down signatures and sudden vertical-rate dips.
            </p>
          </div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#f43f5e', fontSize: 'var(--text-xs)', fontWeight: 600 }}>
            <Lock size={12} aria-hidden="true" />
            <span>Strict Air Safety Confidentiality</span>
          </div>
        </div>

        <div style={{ marginTop: '16px', padding: '12px 16px', borderRadius: '8px', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <AlertTriangle size={16} style={{ color: '#fbbf24', flexShrink: 0 }} aria-hidden="true" />
          <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1', lineHeight: '1.5' }}>
            <strong>Safety &amp; Privacy Guardrail (README Section 7):</strong> This watchlist is private and never exported. It represents an internal investigative hypothesis tool, not proof of anomaly. Tail numbers and real operators are never stored or published.
          </p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '36px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'rgba(51, 65, 85, 0.6)', color: '#94a3b8', marginBottom: '16px' }}>
          <EyeOff size={32} aria-hidden="true" />
        </div>
        <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 'var(--text-lg)', fontWeight: 700 }}>
          0 Active Precursor Candidates
        </h3>
        <p style={{ margin: '0 auto', maxWidth: '480px', color: '#94a3b8', fontSize: 'var(--text-sm)', lineHeight: '1.6' }}>
          Per Phase 0.5 rules, this table is strictly empty until the automated precursor scanner module evaluates candidate flights during Phase 2.
        </p>
      </div>
    </div>
  )
}

