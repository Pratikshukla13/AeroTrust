import { useEffect, useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
  Radio,
  HelpCircle,
  Layers,
  FileText,
  Map as MapIcon,
  Plane,
  Tag,
  Info,
} from 'lucide-react'
import { RouteId } from '../App'

interface TierData {
  count: number
  share_pct: number
  description: string
}

interface SecondaryUnitData {
  unit: string
  count: number
  note: string
}

interface OverviewData {
  tag: string
  active_dataset: string
  dataset_fingerprint: {
    tag: string
    name: string
    seed: string
    flights: number
    n_clean: number
    n_spoof: number
    n_jam: number
    config_hash: string
    primary_unit: string
  }
  primary_unit: string
  tier_distribution: Record<string, TierData>
  secondary_unit?: SecondaryUnitData | null
  headline_box: {
    title: string
    bullets: string[]
  }
  links: Array<{ id: string; label: string; path: string }>
}

interface Props {
  activeDataset: 'benchmark' | 'rule_trigger_demo'
  onNavigate: (route: RouteId) => void
}

export default function OverviewPage({ activeDataset, onNavigate }: Props) {
  const [data, setData] = useState<OverviewData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetch(`/api/overview?dataset=${activeDataset}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`)
        return res.json()
      })
      .then((json: OverviewData) => {
        if (!cancelled) {
          setData(json)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(`Failed to retrieve dynamic metrics: ${err.message}`)
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [activeDataset])

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
        <p style={{ margin: 0, color: '#38bdf8', fontSize: '1rem', fontWeight: 600 }}>
          Retrieving real metrics from API endpoint (/api/overview)...
        </p>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="glass-panel" style={{ padding: '30px', borderLeft: '4px solid #ef4444' }}>
        <h3 style={{ margin: '0 0 8px', color: '#f8fafc', fontSize: '1.125rem' }}>Observatory API Offline</h3>
        <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.875rem' }}>{error}</p>
      </div>
    )
  }

  const { tier_distribution: td, headline_box: hb, dataset_fingerprint: fp } = data

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'flagged_altitude_inconsistency':
        return { text: '#fb7185', bg: 'rgba(251, 113, 133, 0.15)', border: 'rgba(251, 113, 133, 0.4)' }
      case 'jamming_degraded':
        return { text: '#fbbf24', bg: 'rgba(251, 191, 36, 0.12)', border: 'rgba(251, 191, 36, 0.35)' }
      case 'insufficient':
        return { text: '#c084fc', bg: 'rgba(192, 132, 252, 0.15)', border: 'rgba(192, 132, 252, 0.4)' }
      case 'no_alert':
      default:
        return { text: '#34d399', bg: 'rgba(52, 211, 153, 0.12)', border: 'rgba(52, 211, 153, 0.35)' }
    }
  }

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'flagged_altitude_inconsistency':
        return <ShieldAlert size={20} aria-hidden="true" />
      case 'jamming_degraded':
        return <Radio size={20} aria-hidden="true" />
      case 'insufficient':
        return <HelpCircle size={20} aria-hidden="true" />
      case 'no_alert':
      default:
        return <Layers size={20} aria-hidden="true" />
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 1. Headline Box: What this can and cannot do */}
      <div
        className="glass-panel"
        data-testid="headline-limits-box"
        style={{
          padding: '24px 28px',
          borderLeft: '4px solid #38bdf8',
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <div style={{ padding: '6px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
            <AlertTriangle size={18} aria-hidden="true" />
          </div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
            {hb.title}
          </h2>
        </div>

        <ul style={{ margin: 0, paddingLeft: '22px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {hb.bullets.map((bullet, idx) => (
            <li key={idx} style={{ color: '#cbd5e1', fontSize: '0.875rem', lineHeight: 1.55 }}>
              <strong style={{ color: '#f8fafc' }}>{bullet.split(':')[0]}:</strong>
              {bullet.includes(':') ? bullet.slice(bullet.indexOf(':') + 1) : ''}
            </li>
          ))}
        </ul>
      </div>

      {/* 2. Dataset Fingerprint & Release Tag Header */}
      <div
        className="glass-card"
        data-testid="overview-fingerprint-card"
        style={{
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          backgroundColor: 'rgba(30, 41, 59, 0.8)',
          border: '1px solid #334155',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'rgba(56, 189, 248, 0.15)',
              border: '1px solid rgba(56, 189, 248, 0.4)',
              color: '#38bdf8',
              fontSize: '0.8125rem',
              fontWeight: 700,
            }}
          >
            <Tag size={13} aria-hidden="true" />
            <span>Release Tag: {data.tag}</span>
          </span>

          <span style={{ fontSize: '0.875rem', color: '#f8fafc', fontWeight: 600 }}>
            Dataset: {fp.name}
          </span>
          <span style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
            Seed: {fp.seed}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.8125rem', color: '#cbd5e1' }}>
          <span>Primary Unit: <strong style={{ color: '#f8fafc' }}>{data.primary_unit}</strong></span>
          <span style={{ fontFamily: 'monospace', color: '#94a3b8' }}>Hash: {fp.config_hash.slice(0, 10)}...</span>
        </div>
      </div>

      {/* 3. Operational Tier Distribution Cards */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '14px' }}>
          <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
            Operational Evidence Tier Distribution
          </h3>
          <span style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
            Primary Accounting Unit: <strong style={{ color: '#cbd5e1' }}>{data.primary_unit}</strong>
          </span>
        </div>

        <div
          data-testid="tier-distribution-grid"
          style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}
        >
          {Object.entries(td).map(([tierKey, tierInfo]) => {
            const colors = getTierColor(tierKey)
            const icon = getTierIcon(tierKey)
            return (
              <div
                key={tierKey}
                data-testid={`tier-card-${tierKey}`}
                className="glass-card"
                style={{
                  padding: '20px',
                  borderTop: `3px solid ${colors.text}`,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        fontFamily: 'monospace',
                        color: colors.text,
                        backgroundColor: colors.bg,
                        border: `1px solid ${colors.border}`,
                        padding: '3px 8px',
                        borderRadius: '4px',
                      }}
                    >
                      {tierKey}
                    </span>
                    <div style={{ color: colors.text }}>{icon}</div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', margin: '8px 0' }}>
                    <span
                      data-testid={`tier-count-${tierKey}`}
                      style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}
                    >
                      {tierInfo.count.toLocaleString()}
                    </span>
                    <span style={{ fontSize: '0.875rem', fontWeight: 600, color: colors.text }}>
                      ({tierInfo.share_pct.toFixed(2)}%)
                    </span>
                  </div>

                  <p style={{ margin: 0, fontSize: '0.8125rem', color: '#cbd5e1', lineHeight: 1.45 }}>
                    {tierInfo.description}
                  </p>
                </div>

                <div style={{ borderTop: '1px solid #334155', paddingTop: '8px', fontSize: '0.6875rem', color: '#94a3b8' }}>
                  Unit: {data.primary_unit}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* 4. Secondary Continuous Unit Disclosure (Benchmark Only) */}
      {data.secondary_unit && (
        <div
          data-testid="secondary-unit-callout"
          style={{
            padding: '14px 20px',
            backgroundColor: 'rgba(30, 41, 59, 0.6)',
            border: '1px solid #334155',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.8125rem',
            color: '#cbd5e1',
          }}
        >
          <Info size={18} style={{ color: '#38bdf8', flexShrink: 0 }} aria-hidden="true" />
          <div>
            <strong>Distinct Multi-Leg Unit Accounting: </strong>
            Timetable scheduled legs ({fp.flights.toLocaleString()}) are also tracked as continuous airframe routes:
            {' '}<strong style={{ color: '#f8fafc' }}>{data.secondary_unit.count.toLocaleString()} {data.secondary_unit.unit}s</strong>
            {' '}({data.secondary_unit.note}).
          </div>
        </div>
      )}

      {/* 5. Navigation Detail Links */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
          Observatory Modules &amp; Detail Pages
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
          <button
            type="button"
            data-testid="link-to-map"
            onClick={() => onNavigate('map')}
            style={{
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              color: '#f8fafc',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '12px',
              transition: 'background-color 0.15s ease',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', marginBottom: '6px' }}>
                <MapIcon size={18} aria-hidden="true" />
                <strong style={{ fontSize: '0.9375rem' }}>Interference Map</strong>
              </div>
              <p style={{ margin: 0, fontSize: '0.8125rem', color: '#94a3b8', lineHeight: 1.4 }}>
                MapLibre vector view with H3 interference cells and regional filters.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#38bdf8', fontSize: '0.75rem', fontWeight: 600 }}>
              <span>View Map</span>
              <ArrowRight size={14} aria-hidden="true" />
            </div>
          </button>

          <button
            type="button"
            data-testid="link-to-flight-detail"
            onClick={() => onNavigate('flight-detail')}
            style={{
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              color: '#f8fafc',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f43f5e', marginBottom: '6px' }}>
                <Plane size={18} aria-hidden="true" />
                <strong style={{ fontSize: '0.9375rem' }}>Flight Detail</strong>
              </div>
              <p style={{ margin: 0, fontSize: '0.8125rem', color: '#94a3b8', lineHeight: 1.4 }}>
                Single-flight telemetry inspection, checks breakdown, and altitude plot.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#f43f5e', fontSize: '0.75rem', fontWeight: 600 }}>
              <span>Inspect Flights</span>
              <ArrowRight size={14} aria-hidden="true" />
            </div>
          </button>

          <button
            type="button"
            data-testid="link-to-sar"
            onClick={() => onNavigate('sar')}
            style={{
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              color: '#f8fafc',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fbbf24', marginBottom: '6px' }}>
                <ShieldAlert size={18} aria-hidden="true" />
                <strong style={{ fontSize: '0.9375rem' }}>SAR Metrics</strong>
              </div>
              <p style={{ margin: 0, fontSize: '0.8125rem', color: '#94a3b8', lineHeight: 1.4 }}>
                Silent Acceptance Rate by airframe family &times; midpoint region with Wilson intervals.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#fbbf24', fontSize: '0.75rem', fontWeight: 600 }}>
              <span>Analyze SAR</span>
              <ArrowRight size={14} aria-hidden="true" />
            </div>
          </button>

          <button
            type="button"
            data-testid="link-to-limitations"
            onClick={() => onNavigate('limitations')}
            style={{
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              color: '#f8fafc',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34d399', marginBottom: '6px' }}>
                <FileText size={18} aria-hidden="true" />
                <strong style={{ fontSize: '0.9375rem' }}>Limitations &amp; Base Rates</strong>
              </div>
              <p style={{ margin: 0, fontSize: '0.8125rem', color: '#94a3b8', lineHeight: 1.4 }}>
                Boundary disclosures, noise assumptions, and threat prevalence sensitivity.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#34d399', fontSize: '0.75rem', fontWeight: 600 }}>
              <span>Read Limitations</span>
              <ArrowRight size={14} aria-hidden="true" />
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}
