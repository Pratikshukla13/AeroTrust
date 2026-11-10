import { Shield, Hash, Tag, Layers } from 'lucide-react'

export interface DatasetFingerprintData {
  tag: string
  name: string
  seed: string
  flights: number
  n_clean: number
  n_spoof: number
  n_jam: number
  config_hash: string
  primary_unit: string
  secondary_unit?: string | null
}

interface Props {
  fingerprint?: DatasetFingerprintData | null
  tag?: string
}

export default function DatasetFingerprintBar({ fingerprint, tag = 'v0.3.2-verified' }: Props) {
  if (!fingerprint) {
    return (
      <div
        data-testid="dataset-fingerprint-bar"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '6px 16px',
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderBottom: '1px solid #1e293b',
          fontSize: '0.75rem',
          color: '#94a3b8',
        }}
      >
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#38bdf8', fontWeight: 600 }}>
          <Tag size={12} aria-hidden="true" />
          <span>Release Tag: {tag}</span>
        </span>
      </div>
    )
  }

  return (
    <div
      data-testid="dataset-fingerprint-bar"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px',
        padding: '6px 20px',
        backgroundColor: 'rgba(11, 17, 32, 0.95)',
        borderBottom: '1px solid #1e293b',
        fontSize: '0.75rem',
        color: '#cbd5e1',
        zIndex: 30,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', color: '#38bdf8', fontWeight: 700 }}>
          <Tag size={12} aria-hidden="true" />
          <span>Tag: {tag}</span>
        </div>

        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
          <Shield size={12} style={{ color: '#fbbf24' }} aria-hidden="true" />
          <span><strong>Dataset:</strong> {fingerprint.name}</span>
        </div>

        <div>
          <span><strong>Seed:</strong> {fingerprint.seed}</span>
        </div>

        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
          <Layers size={12} style={{ color: '#34d399' }} aria-hidden="true" />
          <span><strong>Flights:</strong> {fingerprint.flights.toLocaleString()} ({fingerprint.primary_unit})</span>
        </div>

        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontFamily: 'monospace', color: '#94a3b8' }}>
          <Hash size={12} aria-hidden="true" />
          <span>Config Hash: {fingerprint.config_hash.slice(0, 12)}...</span>
        </div>
      </div>
    </div>
  )
}

