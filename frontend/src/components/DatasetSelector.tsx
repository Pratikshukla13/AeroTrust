import { Database, CheckCircle2 } from 'lucide-react'

export type DatasetMode = 'benchmark' | 'rule_trigger_demo'

interface Props {
  activeDataset: DatasetMode
  onChangeDataset: (mode: DatasetMode) => void
  disabled?: boolean
}

export default function DatasetSelector({ activeDataset, onChangeDataset, disabled = false }: Props) {
  return (
    <div
      data-testid="dataset-selector"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '3px',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        border: '1px solid #334155',
        borderRadius: '8px',
        gap: '4px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '0 8px', color: '#94a3b8', fontSize: '0.75rem' }}>
        <Database size={13} aria-hidden="true" style={{ color: '#38bdf8' }} />
        <span style={{ fontWeight: 600 }}>Active Cohort:</span>
      </div>

      <button
        type="button"
        data-testid="btn-dataset-benchmark"
        onClick={() => onChangeDataset('benchmark')}
        disabled={disabled}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '5px 10px',
          fontSize: '0.75rem',
          fontWeight: activeDataset === 'benchmark' ? 700 : 500,
          color: activeDataset === 'benchmark' ? '#ffffff' : '#cbd5e1',
          backgroundColor: activeDataset === 'benchmark' ? '#0369a1' : 'transparent',
          border: activeDataset === 'benchmark' ? '1px solid #38bdf8' : '1px solid transparent',
          borderRadius: '6px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.15s ease',
        }}
        aria-pressed={activeDataset === 'benchmark'}
      >
        {activeDataset === 'benchmark' && <CheckCircle2 size={12} aria-hidden="true" />}
        <span>Benchmark (v0.3.2)</span>
      </button>

      <button
        type="button"
        data-testid="btn-dataset-demo"
        onClick={() => onChangeDataset('rule_trigger_demo')}
        disabled={disabled}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '5px 10px',
          fontSize: '0.75rem',
          fontWeight: activeDataset === 'rule_trigger_demo' ? 700 : 500,
          color: activeDataset === 'rule_trigger_demo' ? '#ffffff' : '#cbd5e1',
          backgroundColor: activeDataset === 'rule_trigger_demo' ? '#b45309' : 'transparent',
          border: activeDataset === 'rule_trigger_demo' ? '1px solid #fbbf24' : '1px solid transparent',
          borderRadius: '6px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.15s ease',
        }}
        aria-pressed={activeDataset === 'rule_trigger_demo'}
      >
        {activeDataset === 'rule_trigger_demo' && <CheckCircle2 size={12} aria-hidden="true" />}
        <span>Rule-Trigger Demo (Stress)</span>
      </button>
    </div>
  )
}

