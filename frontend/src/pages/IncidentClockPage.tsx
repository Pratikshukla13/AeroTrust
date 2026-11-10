import { useState, useEffect, useMemo } from 'react'
import {
  Clock,
  Calendar,
  Info,
  ExternalLink,
  RotateCcw,
  TrendingDown,
  Layers,
  DollarSign,
  ShieldAlert,
  GitBranch,
} from 'lucide-react'

export interface DatedEvent {
  date: string
  label: string
  description: string
  source_url?: string | null
  source_type?: string | null
}

export interface SourceItem {
  url: string
  title: string
  source_type: string
  fact_referenced: string
}

export interface FleetBreakdown {
  name: string
  source_url: string
  source_type: string
  in_service?: number | null
  undelivered_or_production?: number | null
  customer_allocated_or_other?: number | null
  total: number
  notes?: string | null
}

export interface IncidentCase {
  case_id: string
  title: string
  event_date: string | null
  public_statement_date: string | null
  directive_date: string | null
  directive_status?: 'issued' | 'effective' | 'proposed' | 'final' | null
  aircraft_affected_total: number | null
  aircraft_in_service: number | null
  aircraft_undelivered: number | null
  deliveries_context: string | null
  in_service_scope_notes?: string | null
  days_event_to_statement: number | null
  source_url: string
  source_type?: string
  sources?: SourceItem[]
  dated_events?: DatedEvent[]
  fleet_breakdowns?: FleetBreakdown[]
  verification_status: 'sourced' | 'needs verification' | 'unknown field'
}

export interface IncidentCasePreset {
  case_id: string
  title: string
  days_to_scope: number | null
  aircraft_held_in_service: number | null
  aircraft_held_undelivered: number | null
  baseline_handover_rate_per_month: number | null
  share_recovered_later: number | null
  value_per_aircraft: number | null
  sourced_fields: string[]
}

const DEFAULT_CASES: IncidentCase[] = [
  {
    case_id: 'A320-SOLAR-2025',
    title: 'A320 Solar Radiation Single-Event Effect',
    event_date: '2025-10-30',
    public_statement_date: '2025-11-28',
    directive_date: '2025-11-28',
    directive_status: 'issued',
    aircraft_affected_total: 6000,
    aircraft_in_service: null,
    aircraft_undelivered: null,
    deliveries_context: 'About 6,000 aircraft, fewer than 100 remaining on 1 Dec 2025.',
    in_service_scope_notes: null,
    days_event_to_statement: 29,
    source_url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
    source_type: 'regulator',
    verification_status: 'needs verification',
    sources: [
      {
        url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
        title: 'EASA Emergency Airworthiness Directive',
        source_type: 'regulator',
        fact_referenced: 'Emergency AD issued 28 Nov 2025 for ~6,000 aircraft; effective date to be confirmed from AD document.',
      },
      {
        url: 'https://www.airbus.com/en/newsroom/press-releases/2025-11-alert-a320-flight-controls',
        title: 'Airbus Alert Notification to Operators',
        source_type: 'manufacturer',
        fact_referenced: 'Airbus alert issued 28 Nov 2025; stated intense solar radiation may corrupt data critical to flight controls; <100 remaining on 1 Dec 2025.',
      },
    ],
    dated_events: [
      {
        date: '2025-10-30',
        label: 'Incident Event',
        description: 'Flight controls data corruption event occurs at cruise altitude. Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts have questioned whether the radiation level on that date was unusual.',
        source_url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
        source_type: 'regulator',
      },
      {
        date: '2025-11-28',
        label: 'Airbus Alert & EASA Emergency AD Issued',
        description: 'Airbus alert and EASA emergency directive issued 28 Nov 2025 (effective date to be confirmed from the AD document).',
        source_url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
        source_type: 'regulator',
      },
      {
        date: '2025-12-01',
        label: 'Rectification Milestone',
        description: 'Fewer than 100 aircraft remaining out of ~6,000 affected.',
        source_url: 'https://www.airbus.com/en/newsroom/press-releases/2025-11-alert-a320-flight-controls',
        source_type: 'manufacturer',
      },
    ],
    fleet_breakdowns: [],
  },
  {
    case_id: 'A320-PANEL-2025',
    title: 'A320 Fuselage Panels Production Discrepancy',
    event_date: null,
    public_statement_date: '2025-12-02',
    directive_date: '2025-12-17',
    directive_status: 'proposed',
    aircraft_affected_total: 628,
    aircraft_in_service: 177,
    aircraft_undelivered: 451,
    deliveries_context: '2025 delivery target cut 820 to 790 on 3 Dec 2025.',
    in_service_scope_notes: null,
    days_event_to_statement: null,
    source_url: 'https://ad.easa.europa.eu/pad/PAD-2025-XXXX',
    source_type: 'regulator',
    verification_status: 'needs verification',
    sources: [
      {
        url: 'https://ad.easa.europa.eu/pad/PAD-2025-XXXX',
        title: 'EASA Proposed Airworthiness Directive (PAD)',
        source_type: 'regulator',
        fact_referenced: 'EASA PROPOSED directive published 17 Dec 2025 (177 in service, 451 in production); later final directive to be confirmed.',
      },
      {
        url: 'https://www.airbus.com/en/newsroom/press-releases/2025-12-a320-quality-update',
        title: 'Airbus Statement on Fuselage Panels',
        source_type: 'manufacturer',
        fact_referenced: 'Airbus public statement 2 Dec 2025 confirming 628 in scope; 2025 delivery target cut 820 to 790 on 3 Dec 2025.',
      },
      {
        url: 'https://www.reuters.com/business/aerospace-defense/airbus-fuselage-panels-breakdown-2025-12',
        title: 'Reuters Investigation & Fleet Breakdown',
        source_type: 'wire',
        fact_referenced: 'Reuters-based fleet split of 628 aircraft: 168 in airline service, 245 at Airbus facilities, 215 customer-allocated.',
      },
    ],
    dated_events: [
      {
        date: '2025-12-02',
        label: 'Airbus Public Statement',
        description: 'Airbus public statement confirming 628 aircraft in scope for fuselage panel discrepancy.',
        source_url: 'https://www.airbus.com/en/newsroom/press-releases/2025-12-a320-quality-update',
        source_type: 'manufacturer',
      },
      {
        date: '2025-12-03',
        label: 'Delivery Target Cut',
        description: 'Airbus officially cuts 2025 delivery target from 820 to 790 aircraft.',
        source_url: 'https://www.airbus.com/en/newsroom/press-releases/2025-12-a320-quality-update',
        source_type: 'manufacturer',
      },
      {
        date: '2025-12-17',
        label: 'EASA PROPOSED Directive Published',
        description: 'EASA publishes PROPOSED directive for 628 aircraft (177 in service, 451 in production; later final directive to be confirmed).',
        source_url: 'https://ad.easa.europa.eu/pad/PAD-2025-XXXX',
        source_type: 'regulator',
      },
    ],
    fleet_breakdowns: [
      {
        name: 'EASA Proposed Directive (17 Dec 2025)',
        source_url: 'https://ad.easa.europa.eu/pad/PAD-2025-XXXX',
        source_type: 'regulator',
        in_service: 177,
        undelivered_or_production: 451,
        total: 628,
        notes: 'Official EASA Proposed Directive regulatory scope: 177 in service, 451 in production.',
      },
      {
        name: 'Reuters Sourced Breakdown (Dec 2025)',
        source_url: 'https://www.reuters.com/business/aerospace-defense/airbus-fuselage-panels-breakdown-2025-12',
        source_type: 'wire',
        in_service: 168,
        undelivered_or_production: 245,
        customer_allocated_or_other: 215,
        total: 628,
        notes: 'Reuters investigative report split: 168 in service, 245 stored/in production, 215 customer-allocated.',
      },
    ],
  },
  {
    case_id: 'A330NEO-TOOL-2026',
    title: 'A330neo Stray Assembly Tool Inspection',
    event_date: null,
    public_statement_date: null,
    directive_date: null,
    directive_status: null,
    aircraft_affected_total: null,
    aircraft_in_service: null,
    aircraft_undelivered: null,
    deliveries_context:
      'Zero deliveries in June and July 2026; 3, 2, 4 in March, April, May; one on 11 Aug 2026; number of aircraft inspected not disclosed; policy to the regulator due mid-November 2026.',
    in_service_scope_notes: 'conflicting reports, needs verification',
    days_event_to_statement: null,
    source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
    source_type: 'manufacturer',
    verification_status: 'needs verification',
    sources: [
      {
        url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        title: 'Airbus Monthly Orders & Deliveries Files (2026)',
        source_type: 'manufacturer',
        fact_referenced: 'Official deliveries: March (3), April (2), May (4); June (0), July (0); 11 Aug 2026 (1).',
      },
      {
        url: 'https://www.easa.europa.eu/en/newsroom-and-events/press-releases/airbus-a330neo-tool-inspection-filing',
        title: 'EASA Regulatory Filing Notice',
        source_type: 'regulator',
        fact_referenced: 'Inspection policy to the regulator due mid-November 2026; scope of in-service inspections subject to conflicting reports, needs verification.',
      },
    ],
    dated_events: [
      {
        date: '2026-03-31',
        label: 'March Deliveries',
        description: '3 A330neo aircraft delivered.',
        source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        source_type: 'manufacturer',
      },
      {
        date: '2026-04-30',
        label: 'April Deliveries',
        description: '2 A330neo aircraft delivered.',
        source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        source_type: 'manufacturer',
      },
      {
        date: '2026-05-31',
        label: 'May Deliveries',
        description: '4 A330neo aircraft delivered (total 9 in March–May).',
        source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        source_type: 'manufacturer',
      },
      {
        date: '2026-06-30',
        label: 'June Delivery Pause',
        description: 'Zero A330neo deliveries during assembly tool inspection pause.',
        source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        source_type: 'manufacturer',
      },
      {
        date: '2026-07-31',
        label: 'July Delivery Pause',
        description: 'Zero A330neo deliveries during continued tool inspection.',
        source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        source_type: 'manufacturer',
      },
      {
        date: '2026-08-11',
        label: 'Deliveries Resume',
        description: 'One A330neo delivered on 11 Aug 2026.',
        source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
        source_type: 'manufacturer',
      },
      {
        date: '2026-11-15',
        label: 'Regulator Filing Milestone',
        description: 'Policy to the regulator due mid-November 2026.',
        source_url: 'https://www.easa.europa.eu/en/newsroom-and-events/press-releases/airbus-a330neo-tool-inspection-filing',
        source_type: 'regulator',
      },
    ],
    fleet_breakdowns: [],
  },
]

export default function IncidentClockPage() {
  const [cases, setCases] = useState<IncidentCase[]>(DEFAULT_CASES)
  const [activePreset, setActivePreset] = useState<string | null>(null)
  const [sourcedFields, setSourcedFields] = useState<string[]>([])

  // User-editable inputs (all blank by default unless loaded from sourced preset)
  const [daysToScope, setDaysToScope] = useState<string>('')
  const [inService, setInService] = useState<string>('')
  const [undelivered, setUndelivered] = useState<string>('')
  const [baselineRate, setBaselineRate] = useState<string>('')
  const [shareRecovered, setShareRecovered] = useState<string>('')
  const [valuePerAircraft, setValuePerAircraft] = useState<string>('')

  useEffect(() => {
    fetch('/api/incident-cases')
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then((data: IncidentCase[]) => {
        if (Array.isArray(data) && data.length > 0) {
          setCases(data)
        }
      })
      .catch(() => {
        // Fallback to DEFAULT_CASES
      })
  }, [])

  // Presets load ONLY sourced parameters; unsourced fields remain empty and visually highlighted
  const handleApplyPreset = (presetId: string) => {
    setActivePreset(presetId)
    if (presetId === 'A320-SOLAR-2025') {
      setDaysToScope('29')
      setInService('')
      setUndelivered('')
      setBaselineRate('')
      setShareRecovered('')
      setValuePerAircraft('')
      setSourcedFields(['days_to_scope'])
    } else if (presetId === 'A320-PANEL-2025') {
      setDaysToScope('')
      setInService('177')
      setUndelivered('451')
      setBaselineRate('')
      setShareRecovered('')
      setValuePerAircraft('')
      setSourcedFields(['aircraft_held_in_service', 'aircraft_held_undelivered'])
    } else if (presetId === 'A330NEO-TOOL-2026' || presetId === 'A330-TOOL-2026') {
      setDaysToScope('')
      setInService('')
      setUndelivered('')
      setBaselineRate('')
      setShareRecovered('')
      setValuePerAircraft('')
      setSourcedFields([])
    } else {
      handleReset()
    }
  }

  const handleReset = () => {
    setActivePreset(null)
    setDaysToScope('')
    setInService('')
    setUndelivered('')
    setBaselineRate('')
    setShareRecovered('')
    setValuePerAircraft('')
    setSourcedFields([])
  }

  // Reactive calculations
  const parsedDays = daysToScope.trim() !== '' ? parseFloat(daysToScope) : null
  const parsedInService = inService.trim() !== '' ? parseFloat(inService) : null
  const parsedUndelivered = undelivered.trim() !== '' ? parseFloat(undelivered) : null
  const parsedBaselineRate = baselineRate.trim() !== '' ? parseFloat(baselineRate) : null
  const parsedShareRecovered = shareRecovered.trim() !== '' ? parseFloat(shareRecovered) / 100.0 : null
  const parsedValue = valuePerAircraft.trim() !== '' ? parseFloat(valuePerAircraft) : null

  const hasHeld = parsedInService !== null || parsedUndelivered !== null
  const totalHeld = hasHeld ? (parsedInService || 0) + (parsedUndelivered || 0) : null

  // a. aircraft_days_held = held aircraft x days
  const aircraftDaysHeld = totalHeld !== null && parsedDays !== null ? totalHeld * parsedDays : null

  // b. Model A (line stop): handovers_lost = baseline_rate x days / 30, net of recovered share
  const modelAGross = parsedBaselineRate !== null && parsedDays !== null ? parsedBaselineRate * (parsedDays / 30.0) : null
  const recFactor = parsedShareRecovered !== null ? 1.0 - parsedShareRecovered : 1.0
  const modelANet = modelAGross !== null ? modelAGross * recFactor : null

  // c. Model B (hold of finished aircraft): handover delay in aircraft-days only
  const modelBAircraftDays =
    parsedUndelivered !== null && parsedDays !== null
      ? parsedUndelivered * parsedDays
      : totalHeld !== null && parsedDays !== null && parsedUndelivered === null
      ? totalHeld * parsedDays
      : null

  // One-day cost of delay (aircraft-days per day)
  const oneDayAircraftDays = totalHeld !== null ? totalHeld : null

  // Financial figures: ONLY if valuePerAircraft is provided (> 0)
  const financialImpactTotal = parsedValue !== null && parsedValue > 0 && modelANet !== null ? modelANet * parsedValue : null
  const oneDayCostMoney =
    parsedValue !== null && parsedValue > 0 && parsedBaselineRate !== null
      ? (parsedBaselineRate / 30.0) * recFactor * parsedValue
      : null

  // Sensitivity table over days (0.5x, 1x, 2x)
  const sensitivityRows = useMemo(() => {
    const mults = [
      { label: '0.5x', factor: 0.5 },
      { label: '1.0x', factor: 1.0 },
      { label: '2.0x', factor: 2.0 },
    ]

    return mults.map(({ label, factor }) => {
      const sDays = parsedDays !== null ? parsedDays * factor : null
      const sHeldDays = totalHeld !== null && sDays !== null ? totalHeld * sDays : null
      const sModelANet =
        parsedBaselineRate !== null && sDays !== null ? parsedBaselineRate * (sDays / 30.0) * recFactor : null
      const sModelBDays =
        parsedUndelivered !== null && sDays !== null
          ? parsedUndelivered * sDays
          : totalHeld !== null && sDays !== null && parsedUndelivered === null
          ? totalHeld * sDays
          : null
      const sMoney =
        parsedValue !== null && parsedValue > 0 && sModelANet !== null ? sModelANet * parsedValue : null

      return {
        label,
        factor,
        days: sDays,
        heldDays: sHeldDays,
        modelANet: sModelANet,
        modelBDays: sModelBDays,
        money: sMoney,
      }
    })
  }, [parsedDays, totalHeld, parsedBaselineRate, recFactor, parsedUndelivered, parsedValue])

  // Helper for unsourced highlight border
  const getFieldStyle = (fieldName: string) => {
    const isSourced = sourcedFields.includes(fieldName)
    if (activePreset && !isSourced) {
      return {
        border: '1px dashed #fbbf24',
        backgroundColor: 'rgba(251, 191, 36, 0.05)',
      }
    }
    return {
      border: '1px solid #334155',
      backgroundColor: '#0f172a',
    }
  }

  const formatCurrency = (val: number | null) => {
    if (val === null) return '--'
    if (val >= 1_000_000_000) {
      return `$${(val / 1_000_000_000).toFixed(2)} B`
    }
    if (val >= 1_000_000) {
      return `$${(val / 1_000_000).toFixed(2)} M`
    }
    return `$${val.toLocaleString()}`
  }

  const getSourceTypeBadge = (sourceType?: string | null) => {
    if (!sourceType) return null
    const map: Record<string, { bg: string; text: string; border: string; label: string }> = {
      regulator: { bg: 'rgba(56, 189, 248, 0.15)', text: '#38bdf8', border: '#0284c7', label: 'EASA / REGULATOR' },
      manufacturer: { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: '#9333ea', label: 'AIRBUS / OEM' },
      wire: { bg: 'rgba(251, 146, 60, 0.15)', text: '#fb923c', border: '#ea580c', label: 'WIRE / REUTERS' },
      media: { bg: 'rgba(148, 163, 184, 0.15)', text: '#cbd5e1', border: '#64748b', label: 'PRESS' },
    }
    const conf = map[sourceType] || map.media
    return (
      <span
        style={{
          fontSize: '0.625rem',
          fontWeight: 700,
          padding: '2px 5px',
          borderRadius: '3px',
          backgroundColor: conf.bg,
          color: conf.text,
          border: `1px solid ${conf.border}`,
          letterSpacing: '0.03em',
        }}
      >
        {conf.label}
      </span>
    )
  }

  const getDirectiveStatusBadge = (status?: string | null) => {
    if (!status) return null
    const map: Record<string, { bg: string; text: string; border: string; label: string }> = {
      issued: { bg: 'rgba(59, 130, 246, 0.15)', text: '#60a5fa', border: '#2563eb', label: 'ISSUED' },
      effective: { bg: 'rgba(34, 197, 94, 0.15)', text: '#4ade80', border: '#16a34a', label: 'EFFECTIVE' },
      proposed: { bg: 'rgba(234, 179, 8, 0.15)', text: '#fde047', border: '#ca8a04', label: 'PROPOSED' },
      final: { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: '#9333ea', label: 'FINAL' },
    }
    const conf = map[status] || map.proposed
    return (
      <span
        data-testid={`badge-directive-status-${status}`}
        style={{
          fontSize: '0.625rem',
          fontWeight: 700,
          padding: '2px 6px',
          borderRadius: '3px',
          backgroundColor: conf.bg,
          color: conf.text,
          border: `1px solid ${conf.border}`,
          letterSpacing: '0.04em',
        }}
      >
        DIRECTIVE: {conf.label}
      </span>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 1. Mandatory Phase 7 Copy Banner */}
      <div
        data-testid="calculator-mandated-copy"
        className="glass-panel"
        style={{
          padding: '16px 20px',
          borderLeft: '4px solid #38bdf8',
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px',
        }}
      >
        <Info size={20} style={{ color: '#38bdf8', flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
        <div>
          <p
            style={{
              margin: 0,
              fontSize: 'var(--text-sm)',
              color: '#f8fafc',
              lineHeight: 1.6,
              fontWeight: 500,
            }}
          >
            This calculator turns public information into a scenario. It does not describe Airbus internal data or
            decisions. Scenario outputs depend on the inputs you enter.
          </p>
        </div>
      </div>

      {/* Header with Mandatory Radiation Disclosure Copy */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <Clock size={24} style={{ color: '#38bdf8' }} aria-hidden="true" />
          <h2 style={{ margin: 0, fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
            Incident Clock &amp; Scoping Cost Calculator
          </h2>
        </div>
        <p style={{ margin: '0 0 14px', fontSize: 'var(--text-sm)', color: '#94a3b8', lineHeight: 1.5 }}>
          Transparent scenario modeller pricing the operational duration and delivery consequences of slow scoping
          using public regulatory milestones. All inputs are editable; presets fill only sourced facts.
        </p>

        {/* Phase 7.1 Mandatory Radiation Context Box */}
        <div
          data-testid="radiation-mandatory-copy"
          style={{
            padding: '12px 16px',
            borderRadius: '6px',
            backgroundColor: 'rgba(30, 41, 59, 0.7)',
            border: '1px solid #475569',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
          }}
        >
          <ShieldAlert size={18} style={{ color: '#fbbf24', flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
          <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#f8fafc', lineHeight: 1.6 }}>
            <strong>Radiation Disclosure &amp; Scope:</strong> Airbus stated that intense solar radiation may corrupt
            data critical to flight controls. Independent experts have questioned whether the radiation level on that
            date was unusual. Axis B is exposure context, not a cause.
          </p>
        </div>
      </div>

      {/* 2. Public Seed Cases Grid with Dated Events & Sourced Breakdowns */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc' }}>
            Public Incident Ground Truth Cases
          </h3>
          <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
            All cases tagged &quot;needs verification&quot; until URLs are user-confirmed.
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '16px' }}>
          {cases.map((c) => (
            <div
              key={c.case_id}
              className="glass-card"
              style={{
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '16px',
                border: '1px solid rgba(148, 163, 184, 0.15)',
              }}
            >
              <div>
                {/* Header row: Case ID + Badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8' }}>{c.case_id}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {getDirectiveStatusBadge(c.directive_status)}
                    <span
                      data-testid={`badge-verification-${c.case_id}`}
                      style={{
                        fontSize: '0.625rem',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: '3px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        backgroundColor:
                          c.verification_status === 'sourced'
                            ? 'rgba(34, 197, 94, 0.15)'
                            : 'rgba(251, 191, 36, 0.15)',
                        color: c.verification_status === 'sourced' ? '#4ade80' : '#fbbf24',
                        border: `1px solid ${c.verification_status === 'sourced' ? '#22c55e' : '#f59e0b'}`,
                      }}
                    >
                      {c.verification_status}
                    </span>
                  </div>
                </div>

                <h4 style={{ margin: '0 0 10px', color: '#f8fafc', fontSize: 'var(--text-base)', fontWeight: 700 }}>
                  {c.title}
                </h4>

                {/* Core Facts Summary */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Event Date:</span>
                    <span>{c.event_date || 'unknown'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Public Statement:</span>
                    <span>{c.public_statement_date || 'unknown'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Directive Date:</span>
                    <span>{c.directive_date || 'to be confirmed'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Aircraft Affected:</span>
                    <span>{c.aircraft_affected_total !== null ? c.aircraft_affected_total.toLocaleString() : 'not disclosed'}</span>
                  </div>
                  {c.aircraft_in_service !== null && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>In Service:</span>
                      <span>{c.aircraft_in_service.toLocaleString()}</span>
                    </div>
                  )}
                  {c.aircraft_undelivered !== null && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Undelivered / In Production:</span>
                      <span>{c.aircraft_undelivered.toLocaleString()}</span>
                    </div>
                  )}
                  {c.in_service_scope_notes && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>In-Service Scope:</span>
                      <span style={{ color: '#fbbf24', fontWeight: 600 }}>{c.in_service_scope_notes}</span>
                    </div>
                  )}
                  {c.days_event_to_statement !== null && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Event-to-Statement Gap:</span>
                      <span style={{ fontWeight: 700, color: '#38bdf8' }}>{c.days_event_to_statement} days</span>
                    </div>
                  )}
                  {c.deliveries_context && (
                    <div style={{ marginTop: '4px', padding: '6px 8px', borderRadius: '4px', backgroundColor: 'rgba(30, 41, 59, 0.6)' }}>
                      <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>{c.deliveries_context}</span>
                    </div>
                  )}
                </div>

                {/* Alternate Sourced Fleet Breakdowns (e.g. for A320 Panels) */}
                {c.fleet_breakdowns && c.fleet_breakdowns.length > 0 && (
                  <div style={{ marginTop: '12px', borderTop: '1px solid #1e293b', paddingTop: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                      <GitBranch size={13} style={{ color: '#38bdf8' }} aria-hidden="true" />
                      <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                        Sourced Fleet Breakdowns
                      </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {c.fleet_breakdowns.map((b, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: '8px 10px',
                            borderRadius: '4px',
                            backgroundColor: 'rgba(15, 23, 42, 0.6)',
                            border: '1px solid #334155',
                            fontSize: 'var(--text-xs)',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                            <strong style={{ color: '#f8fafc' }}>{b.name}</strong>
                            {getSourceTypeBadge(b.source_type)}
                          </div>
                          <div style={{ color: '#cbd5e1' }}>
                            {b.in_service !== null && <span>{b.in_service} in service | </span>}
                            {b.undelivered_or_production !== null && <span>{b.undelivered_or_production} production/undelivered</span>}
                            {b.customer_allocated_or_other !== null && <span> | {b.customer_allocated_or_other} customer-allocated</span>}
                            <span> (Total: {b.total})</span>
                          </div>
                          {b.notes && <div style={{ fontSize: '0.6875rem', color: '#94a3b8', marginTop: '3px' }}>{b.notes}</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Dated Events Milestone List */}
                {c.dated_events && c.dated_events.length > 0 && (
                  <div style={{ marginTop: '12px', borderTop: '1px solid #1e293b', paddingTop: '10px' }}>
                    <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                      Dated Timeline Milestones
                    </span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                      {c.dated_events.map((evt, idx) => (
                        <div
                          key={idx}
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '2px',
                            fontSize: 'var(--text-xs)',
                            borderLeft: '2px solid #38bdf8',
                            paddingLeft: '8px',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <code style={{ color: '#38bdf8', fontSize: '0.6875rem' }}>{evt.date}</code>
                            <strong style={{ color: '#f8fafc' }}>{evt.label}</strong>
                            {getSourceTypeBadge(evt.source_type)}
                          </div>
                          <span style={{ color: '#cbd5e1', fontSize: '0.6875rem' }}>{evt.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Sourced URLs Section */}
              <div style={{ borderTop: '1px solid #1e293b', paddingTop: '10px' }}>
                <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
                  REGULATORY &amp; PRIMARY SOURCES
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {c.sources && c.sources.length > 0 ? (
                    c.sources.map((src, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px' }}>
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: 'var(--text-xs)',
                            color: '#38bdf8',
                            textDecoration: 'none',
                            fontWeight: 600,
                          }}
                        >
                          <span>{src.title}</span>
                          <ExternalLink size={11} aria-hidden="true" />
                        </a>
                        {getSourceTypeBadge(src.source_type)}
                      </div>
                    ))
                  ) : (
                    <a
                      href={c.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: 'var(--text-xs)',
                        color: '#38bdf8',
                        textDecoration: 'none',
                        fontWeight: 600,
                      }}
                    >
                      <span>Primary Source Document</span>
                      <ExternalLink size={11} aria-hidden="true" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. A320 Solar Radiation Timeline View */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Calendar size={20} style={{ color: '#fbbf24' }} aria-hidden="true" />
          <h3 style={{ margin: 0, fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc' }}>
            A320 Solar Radiation Single-Event Effect: Public Disclosure Timeline
          </h3>
        </div>

        {/* Milestone Steps */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '16px',
            marginBottom: '16px',
          }}
        >
          <div style={{ padding: '14px 16px', borderRadius: '8px', backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid #334155' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8', fontWeight: 600 }}>T0: Incident Event</span>
            <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>30 Oct 2025</div>
            <p style={{ margin: '4px 0 0', fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
              Data corruption event critical to flight controls occurs at cruise altitude.
            </p>
          </div>

          <div style={{ padding: '14px 16px', borderRadius: '8px', backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid #334155' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8', fontWeight: 600 }}>T1: Alert &amp; Emergency AD</span>
            <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>28 Nov 2025</div>
            <p style={{ margin: '4px 0 0', fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
              Airbus alert and EASA emergency directive issued (effective date to be confirmed from the AD document).
            </p>
          </div>

          <div style={{ padding: '14px 16px', borderRadius: '8px', backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid #334155' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8', fontWeight: 600 }}>T2: Fleet Rectification</span>
            <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>1 Dec 2025</div>
            <p style={{ margin: '4px 0 0', fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
              Fewer than 100 aircraft remaining out of ~6,000 in scope.
            </p>
          </div>

          <div style={{ padding: '14px 16px', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: '#38bdf8', fontWeight: 700 }}>Computed Public Gap</span>
            <div style={{ fontSize: 'var(--text-xl)', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>29 Days</div>
            <p style={{ margin: '4px 0 0', fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
              Elapsed days between event date (30 Oct) and public alert (28 Nov).
            </p>
          </div>
        </div>

        {/* Timeline Disclosure Copy */}
        <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#94a3b8', fontStyle: 'italic', lineHeight: 1.5 }}>
          Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts
          have questioned whether the radiation level on that date was unusual. Axis B is exposure context, not a cause.
          This timeline is compiled strictly from public regulatory documents and corporate statements.
        </p>
      </div>

      {/* 4. Interactive Calculator Shell */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
          <div>
            <h3 style={{ margin: '0 0 4px', fontSize: 'var(--text-lg)', fontWeight: 700, color: '#f8fafc' }}>
              Scoping Scenario Modeller
            </h3>
            <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
              Choose a public preset to fill sourced numbers, or enter custom parameters.
            </p>
          </div>

          {/* Preset Buttons */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            <button
              type="button"
              data-testid="btn-preset-solar"
              onClick={() => handleApplyPreset('A320-SOLAR-2025')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                cursor: 'pointer',
                backgroundColor: activePreset === 'A320-SOLAR-2025' ? '#0284c7' : '#1e293b',
                color: '#f8fafc',
                border: activePreset === 'A320-SOLAR-2025' ? '1px solid #38bdf8' : '1px solid #475569',
              }}
            >
              Preset: A320 Solar (29 Days)
            </button>
            <button
              type="button"
              data-testid="btn-preset-panel"
              onClick={() => handleApplyPreset('A320-PANEL-2025')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                cursor: 'pointer',
                backgroundColor: activePreset === 'A320-PANEL-2025' ? '#0284c7' : '#1e293b',
                color: '#f8fafc',
                border: activePreset === 'A320-PANEL-2025' ? '1px solid #38bdf8' : '1px solid #475569',
              }}
            >
              Preset: A320 Panels (177 In-Service / 451 Production)
            </button>
            <button
              type="button"
              data-testid="btn-preset-tool"
              onClick={() => handleApplyPreset('A330NEO-TOOL-2026')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                cursor: 'pointer',
                backgroundColor: activePreset === 'A330NEO-TOOL-2026' || activePreset === 'A330-TOOL-2026' ? '#0284c7' : '#1e293b',
                color: '#f8fafc',
                border: activePreset === 'A330NEO-TOOL-2026' || activePreset === 'A330-TOOL-2026' ? '1px solid #38bdf8' : '1px solid #475569',
              }}
            >
              Preset: A330neo (Context Only)
            </button>
            <button
              type="button"
              data-testid="btn-reset-inputs"
              onClick={handleReset}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                cursor: 'pointer',
                backgroundColor: 'transparent',
                color: '#cbd5e1',
                border: '1px solid #475569',
              }}
            >
              <RotateCcw size={12} aria-hidden="true" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Inputs Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {/* Days to Scope */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-days-to-scope" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Days to Scope
              </label>
              {activePreset && !sourcedFields.includes('days_to_scope') && (
                <span style={{ fontSize: '0.6875rem', color: '#fbbf24', fontWeight: 600 }}>Empty (unsourced)</span>
              )}
            </div>
            <input
              id="input-days-to-scope"
              data-testid="input-days-to-scope"
              type="number"
              placeholder="e.g. 29"
              value={daysToScope}
              onChange={(e) => setDaysToScope(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
                outline: 'none',
                ...getFieldStyle('days_to_scope'),
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Elapsed duration of technical or regulatory scoping.</span>
          </div>

          {/* Aircraft Held In Service */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-in-service" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Aircraft Held In-Service
              </label>
              {activePreset && !sourcedFields.includes('aircraft_held_in_service') && (
                <span style={{ fontSize: '0.6875rem', color: '#fbbf24', fontWeight: 600 }}>Empty (unsourced)</span>
              )}
            </div>
            <input
              id="input-in-service"
              data-testid="input-in-service"
              type="number"
              placeholder="e.g. 177"
              value={inService}
              onChange={(e) => setInService(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
                outline: 'none',
                ...getFieldStyle('aircraft_held_in_service'),
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Active fleet units undergoing mandatory inspection.</span>
          </div>

          {/* Aircraft Held Undelivered */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-undelivered" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Aircraft Held Undelivered
              </label>
              {activePreset && !sourcedFields.includes('aircraft_held_undelivered') && (
                <span style={{ fontSize: '0.6875rem', color: '#fbbf24', fontWeight: 600 }}>Empty (unsourced)</span>
              )}
            </div>
            <input
              id="input-undelivered"
              data-testid="input-undelivered"
              type="number"
              placeholder="e.g. 451"
              value={undelivered}
              onChange={(e) => setUndelivered(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
                outline: 'none',
                ...getFieldStyle('aircraft_held_undelivered'),
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Produced airframes paused before customer handover.</span>
          </div>

          {/* Baseline Handover Rate Per Month (Blank by default) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-baseline-rate" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Baseline Handover Rate / Month
              </label>
              <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Optional</span>
            </div>
            <input
              id="input-baseline-rate"
              data-testid="input-baseline-rate"
              type="number"
              placeholder="Blank by default (e.g. 60)"
              value={baselineRate}
              onChange={(e) => setBaselineRate(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
                outline: 'none',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Expected monthly factory production cadence.</span>
          </div>

          {/* Share Recovered Later (Blank by default) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-share-recovered" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Share Recovered Later (%)
              </label>
              <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Optional</span>
            </div>
            <input
              id="input-share-recovered"
              data-testid="input-share-recovered"
              type="number"
              placeholder="Blank by default (e.g. 20%)"
              value={shareRecovered}
              onChange={(e) => setShareRecovered(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
                outline: 'none',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Fraction of delayed deliveries recouped via post-incident overtime.</span>
          </div>

          {/* Value Per Aircraft (Blank by default, optional) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-value-per-aircraft" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Value Per Aircraft ($)
              </label>
              <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>Optional (Financial)</span>
            </div>
            <input
              id="input-value-per-aircraft"
              data-testid="input-value-per-aircraft"
              type="number"
              placeholder="Blank by default (no money shown)"
              value={valuePerAircraft}
              onChange={(e) => setValuePerAircraft(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
                outline: 'none',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>If left blank, zero financial numbers will be displayed.</span>
          </div>
        </div>

        {/* 5. Outputs Section */}
        <h3 style={{ margin: '0 0 14px', fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc' }}>
          Scenario Outputs &amp; Mathematical Formulations
        </h3>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {/* Output A: Aircraft-Days Held */}
          <div
            data-testid="output-card-aircraft-days-held"
            style={{
              padding: '18px',
              borderRadius: '8px',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid #334155',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <Layers size={16} style={{ color: '#38bdf8' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8' }}>Output (a)</span>
              </div>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: '#cbd5e1' }}>Total Aircraft-Days Held</div>
              <div
                data-testid="val-aircraft-days-held"
                style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '8px 0' }}
              >
                {aircraftDaysHeld !== null ? `${aircraftDaysHeld.toLocaleString()} days` : '--'}
              </div>
            </div>
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8', borderTop: '1px solid #1e293b', paddingTop: '8px' }}>
              <div><strong>Formula:</strong> <code>held_aircraft × days_to_scope</code></div>
              <div style={{ marginTop: '2px' }}><strong>Assumption:</strong> Assumes all held aircraft remain unavailable for full duration.</div>
            </div>
          </div>

          {/* Output B: Model A (Line Stop) */}
          <div
            data-testid="output-card-model-a"
            style={{
              padding: '18px',
              borderRadius: '8px',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid #334155',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <TrendingDown size={16} style={{ color: '#f59e0b' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8' }}>Output (b): Model A</span>
              </div>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: '#cbd5e1' }}>Handovers Lost (Line Stop)</div>
              <div
                data-testid="val-model-a-net"
                style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f59e0b', margin: '8px 0' }}
              >
                {modelANet !== null ? `${modelANet.toFixed(1)} aircraft` : '--'}
              </div>
              {modelAGross !== null && parsedShareRecovered !== null && (
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>
                  Gross: {modelAGross.toFixed(1)} | Recovered: {(parsedShareRecovered * 100).toFixed(0)}%
                </div>
              )}
            </div>
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8', borderTop: '1px solid #1e293b', paddingTop: '8px' }}>
              <div><strong>Formula:</strong> <code>(rate × days / 30) × (1 - share_recovered)</code></div>
              <div style={{ marginTop: '2px' }}><strong>Assumption:</strong> 30 days/month even cadence. Requires baseline rate input.</div>
            </div>
          </div>

          {/* Output C: Model B (Hold of Finished Aircraft) */}
          <div
            data-testid="output-card-model-b"
            style={{
              padding: '18px',
              borderRadius: '8px',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid #334155',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <Clock size={16} style={{ color: '#a855f7' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8' }}>Output (c): Model B</span>
              </div>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: '#cbd5e1' }}>Handover Delay (Finished Aircraft)</div>
              <div
                data-testid="val-model-b-days"
                style={{ fontSize: '1.75rem', fontWeight: 800, color: '#c084fc', margin: '8px 0' }}
              >
                {modelBAircraftDays !== null ? `${modelBAircraftDays.toLocaleString()} a/c-days` : '--'}
              </div>
            </div>
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8', borderTop: '1px solid #1e293b', paddingTop: '8px' }}>
              <div><strong>Formula:</strong> <code>aircraft_held_undelivered × days_to_scope</code></div>
              <div style={{ marginTop: '2px' }}><strong>Assumption:</strong> Delivery slippage measured in aircraft-days only.</div>
            </div>
          </div>

          {/* Output D: Financial Impact (Only shown if value_per_aircraft is provided) */}
          <div
            data-testid="output-card-financial"
            style={{
              padding: '18px',
              borderRadius: '8px',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid #334155',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <DollarSign size={16} style={{ color: parsedValue ? '#4ade80' : '#94a3b8' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8' }}>Output (d): Valuation Impact</span>
              </div>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: '#cbd5e1' }}>Total Financial Impact</div>
              <div
                data-testid="val-financial-impact"
                style={{
                  fontSize: '1.75rem',
                  fontWeight: 800,
                  color: parsedValue ? '#4ade80' : '#94a3b8',
                  margin: '8px 0',
                }}
              >
                {formatCurrency(financialImpactTotal)}
              </div>
            </div>
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8', borderTop: '1px solid #1e293b', paddingTop: '8px' }}>
              <div><strong>Formula:</strong> <code>net_handovers_lost × value_per_aircraft</code></div>
              <div style={{ marginTop: '2px' }}>
                {parsedValue ? (
                  <span style={{ color: '#4ade80' }}>Based on user-entered aircraft valuation.</span>
                ) : (
                  <span>No value entered. Per Phase 7 rule, no money figure is shown without user input.</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* One-Day Cost of Delay Callout */}
        <div
          data-testid="callout-one-day-cost"
          style={{
            padding: '14px 18px',
            borderRadius: '8px',
            backgroundColor: 'rgba(30, 41, 59, 0.6)',
            border: '1px solid #475569',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
            marginBottom: '24px',
          }}
        >
          <div>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
              One-Day Cost of Delay
            </span>
            <div style={{ fontSize: 'var(--text-sm)', color: '#f8fafc', marginTop: '2px' }}>
              Incremental delay added for every additional 24 hours of scoping:
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div data-testid="val-one-day-aircraft-days" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>
              {oneDayAircraftDays !== null ? `${oneDayAircraftDays.toLocaleString()} aircraft-days / day` : '--'}
            </div>
            <div data-testid="val-one-day-money" style={{ fontSize: 'var(--text-xs)', color: parsedValue ? '#4ade80' : '#94a3b8' }}>
              {parsedValue ? `Financial rate: ${formatCurrency(oneDayCostMoney)} / day` : 'No money figure (enter value per aircraft to view)'}
            </div>
          </div>
        </div>

        {/* 6. Sensitivity Table over Days (0.5x, 1x, 2x) */}
        <div>
          <h4 style={{ margin: '0 0 10px', fontSize: 'var(--text-sm)', fontWeight: 700, color: '#f8fafc' }}>
            Days to Scope Sensitivity Matrix (0.5x, 1x, 2x)
          </h4>
          <div style={{ overflowX: 'auto' }}>
            <table
              data-testid="sensitivity-table"
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: 'var(--text-xs)',
                textAlign: 'left',
              }}
            >
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '8px 12px' }}>Multiplier</th>
                  <th style={{ padding: '8px 12px' }}>Scoping Duration</th>
                  <th style={{ padding: '8px 12px' }}>Aircraft-Days Held</th>
                  <th style={{ padding: '8px 12px' }}>Model A: Net Lost</th>
                  <th style={{ padding: '8px 12px' }}>Model B: Handover Delay</th>
                  <th style={{ padding: '8px 12px' }}>Financial Impact</th>
                </tr>
              </thead>
              <tbody>
                {sensitivityRows.map((row) => (
                  <tr key={row.label} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 700, color: '#38bdf8' }}>{row.label}</td>
                    <td style={{ padding: '10px 12px', color: '#f8fafc' }}>
                      {row.days !== null ? `${row.days.toFixed(1)} days` : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#cbd5e1' }}>
                      {row.heldDays !== null ? `${row.heldDays.toLocaleString()} a/c-days` : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#f59e0b' }}>
                      {row.modelANet !== null ? `${row.modelANet.toFixed(1)} a/c` : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#c084fc' }}>
                      {row.modelBDays !== null ? `${row.modelBDays.toLocaleString()} a/c-days` : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: row.money ? '#4ade80' : '#94a3b8' }}>
                      {formatCurrency(row.money)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
