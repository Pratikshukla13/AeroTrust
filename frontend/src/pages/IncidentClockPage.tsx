import { Clock, Calculator } from 'lucide-react'

export default function IncidentClockPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h2 style={{ margin: '0 0 8px', fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
          Incident Clock &amp; Scoping Cost Calculator
        </h2>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
          Prices the operational and delivery cost of slow incident scoping using Airbus's public regulatory milestones.
        </p>
      </div>

      {/* Public Seed Cases Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#fbbf24' }}>Case A320-SOLAR-2025</span>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>29 Days Scoping</span>
          </div>
          <h4 style={{ margin: '0 0 6px', color: '#f8fafc', fontSize: 'var(--text-base)' }}>Solar Radiation SEE Incident</h4>
          <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1', lineHeight: '1.5' }}>
            Incident 30 Oct 2025; Airbus statement 28 Nov 2025; Emergency AD 29 Nov 2025. ~6,000 aircraft scoped.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#38bdf8' }}>Case A320-PANEL-2025</span>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>16 Days Scoping</span>
          </div>
          <h4 style={{ margin: '0 0 6px', color: '#f8fafc', fontSize: 'var(--text-base)' }}>Fuselage Panels Discrepancy</h4>
          <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1', lineHeight: '1.5' }}>
            EASA Directive 17 Dec 2025. 628 aircraft affected (177 in service, 451 undelivered). Target revised from 820 to 790.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#fb7185' }}>Case A330-TOOL-2026</span>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>75 Days Scoping</span>
          </div>
          <h4 style={{ margin: '0 0 6px', color: '#f8fafc', fontSize: 'var(--text-base)' }}>Stray Assembly Tool</h4>
          <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1', lineHeight: '1.5' }}>
            Zero A330 deliveries in June and July 2026; 9 in March–May. Inspection policy submitted to EASA mid-Nov 2026.
          </p>
        </div>
      </div>

      {/* Interactive Calculator Shell (Empty State) */}
      <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '16px', borderRadius: '50%', backgroundColor: 'rgba(251, 191, 36, 0.1)', color: '#fbbf24', marginBottom: '16px' }}>
          <Calculator size={32} aria-hidden="true" />
        </div>
        <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: 'var(--text-lg)', fontWeight: 700 }}>
          Interactive Clock Simulator (Next Tier)
        </h3>
        <p style={{ margin: '0 auto 16px', maxWidth: '500px', color: '#94a3b8', fontSize: 'var(--text-sm)', lineHeight: '1.6' }}>
          Allows executive users to simulate aircraft-days held and delivery slips by adjusting days to scope and handover rates across fleet families.
        </p>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', borderRadius: '6px', backgroundColor: 'rgba(51, 65, 85, 0.5)', color: '#cbd5e1', fontSize: 'var(--text-xs)' }}>
          <Clock size={14} style={{ color: '#fbbf24' }} aria-hidden="true" />
          <span>Calculator engine will be activated in Next Tier per README Schedule.</span>
        </div>
      </div>
    </div>
  )
}
