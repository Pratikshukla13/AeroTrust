import { AlertTriangle } from 'lucide-react'

export default function SyntheticBanner() {
  return (
    <aside
      aria-label="Synthetic Simulation Data Disclosure"
      role="alert"
      data-testid="synthetic-banner"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backgroundColor: '#991b1b',
        borderBottom: '1px solid #dc2626',
        color: '#ffffff',
        padding: '8px 16px',
        fontSize: '0.8125rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
      }}
    >
      <AlertTriangle size={16} aria-hidden="true" style={{ flexShrink: 0, color: '#fef08a' }} />
      <span>
        SYNTHETIC DATA MODE ACTIVE — Results on synthetic data demonstrate the method, not real-world accuracy.
      </span>
    </aside>
  )
}

