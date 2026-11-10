import { FileText, Clock } from 'lucide-react'

export default function BriefingPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h1 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
          Briefing (planned, not in this release)
        </h1>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
          Executive synthesis of 24h interference events and radiation exposure context. Status: planned, not implemented.
        </p>
      </div>

      {/* Planned Notice */}
      <div className="glass-panel" style={{ padding: '28px 32px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'rgba(148, 163, 184, 0.1)', color: '#94a3b8', marginBottom: '16px' }}>
          <Clock size={32} aria-hidden="true" />
        </div>
        <h2 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 'var(--text-lg)', fontWeight: 700 }}>
          Briefing Pipeline (Planned, Not Implemented)
        </h2>
        <p style={{ margin: '0 auto 16px', maxWidth: '520px', color: '#94a3b8', fontSize: 'var(--text-sm)', lineHeight: '1.6' }}>
          This feature is planned, not implemented. In future releases, the automated verifier is designed to extract numbers from verified database tables and reject ungrounded figures before display.
        </p>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'rgba(51, 65, 85, 0.5)', color: '#cbd5e1', fontSize: 'var(--text-xs)' }}>
          <FileText size={14} style={{ color: '#94a3b8' }} aria-hidden="true" />
          <span>Feature planned, not implemented in this release.</span>
        </div>
      </div>
    </div>
  )
}
