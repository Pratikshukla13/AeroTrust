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
  AlertTriangle,
} from 'lucide-react'

export interface DatedEvent {
  date: string
  label: string
  description: string
  source_url?: string | null
  source_type?: string | null
  url_status?: 'unchecked' | 'verified by user'
}

export interface SourceItem {
  url?: string | null
  title: string
  source_type: string
  fact_referenced: string
  url_status?: 'unchecked' | 'verified by user'
}

export interface FleetBreakdown {
  name: string
  source_url?: string | null
  source_type: string
  in_service?: number | null
  undelivered_or_production?: number | null
  customer_allocated_or_other?: number | null
  total: number
  notes?: string | null
  url_status?: 'unchecked' | 'verified by user'
}

export interface IncidentCase {
  case_id: string
  title: string
  event_date: string | null
  public_statement_date: string | null
  directive_date: string | null
  directive_status?: 'issued' | 'effective' | 'proposed' | 'final' | 'none_published_or_unknown' | null
  aircraft_affected_total: number | null
  aircraft_in_service: number | null
  aircraft_undelivered: number | null
  deliveries_context: string | null
  in_service_scope_notes?: string | null
  days_event_to_statement: number | null
  source_url: string | null
  source_type?: string
  url_status?: 'unchecked' | 'verified by user'
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
  days_event_to_public_statement?: number | null
  days_event_to_public_statement_helper?: string | null
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
    source_url: null,
    source_type: 'regulator',
    url_status: 'unchecked',
    verification_status: 'needs verification',
    sources: [
      {
        url: null,
        title: 'EASA Emergency Airworthiness Directive',
        source_type: 'regulator',
        url_status: 'unchecked',
        fact_referenced: 'Emergency AD issued 28 Nov 2025 for ~6,000 aircraft; effective date to be confirmed from AD document.',
      },
      {
        url: null,
        title: 'Airbus Alert Notification to Operators',
        source_type: 'manufacturer',
        url_status: 'unchecked',
        fact_referenced: 'Airbus alert issued 28 Nov 2025; stated intense solar radiation may corrupt data critical to flight controls; <100 remaining on 1 Dec 2025.',
      },
    ],
    dated_events: [
      {
        date: '2025-10-30',
        label: 'Incident Event',
        description: 'Flight controls data corruption event occurs at cruise altitude. Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts have questioned whether the radiation level on that date was unusual. Axis B is exposure context, not a cause.',
        source_url: null,
        source_type: 'regulator',
        url_status: 'unchecked',
      },
      {
        date: '2025-11-28',
        label: 'Airbus Alert & EASA Emergency AD Issued',
        description: 'Airbus alert and EASA emergency directive issued 28 Nov 2025 (effective date to be confirmed from the AD document).',
        source_url: null,
        source_type: 'regulator',
        url_status: 'unchecked',
      },
      {
        date: '2025-12-01',
        label: 'Rectification Milestone',
        description: 'Fewer than 100 aircraft remaining out of ~6,000 affected.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
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
    source_url: null,
    source_type: 'regulator',
    url_status: 'unchecked',
    verification_status: 'needs verification',
    sources: [
      {
        url: null,
        title: 'EASA Proposed Airworthiness Directive (PAD)',
        source_type: 'regulator',
        url_status: 'unchecked',
        fact_referenced: 'EASA PROPOSED directive published 17 Dec 2025 (177 in service, 451 in production); later final directive to be confirmed.',
      },
      {
        url: null,
        title: 'Airbus Statement on Fuselage Panels',
        source_type: 'manufacturer',
        url_status: 'unchecked',
        fact_referenced: 'Airbus public statement 2 Dec 2025 confirming 628 in scope; 2025 delivery target cut 820 to 790 on 3 Dec 2025.',
      },
      {
        url: null,
        title: 'Reuters Investigation & Fleet Breakdown',
        source_type: 'wire',
        url_status: 'unchecked',
        fact_referenced: 'Reuters breakdown: 168 in service, 245 on assembly lines (about 100 due for delivery in 2025), 215 in earlier production.',
      },
    ],
    dated_events: [
      {
        date: '2025-12-02',
        label: 'Airbus Public Statement',
        description: 'Airbus public statement confirming 628 aircraft in scope for fuselage panel discrepancy.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2025-12-03',
        label: 'Delivery Target Cut',
        description: 'Airbus officially cuts 2025 delivery target from 820 to 790 aircraft.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2025-12-17',
        label: 'EASA PROPOSED Directive Published',
        description: 'EASA publishes PROPOSED directive for 628 aircraft (177 in service, 451 in production; later final directive to be confirmed).',
        source_url: null,
        source_type: 'regulator',
        url_status: 'unchecked',
      },
    ],
    fleet_breakdowns: [
      {
        name: 'EASA Proposed Directive (17 Dec 2025)',
        source_url: null,
        source_type: 'regulator',
        url_status: 'unchecked',
        in_service: 177,
        undelivered_or_production: 451,
        total: 628,
        notes: 'Official EASA Proposed Directive regulatory scope: 177 in service, 451 in production.',
      },
      {
        name: 'Reuters Sourced Breakdown',
        source_url: null,
        source_type: 'wire',
        url_status: 'unchecked',
        in_service: 168,
        undelivered_or_production: 245,
        customer_allocated_or_other: 215,
        total: 628,
        notes: '168 in service, 245 on assembly lines (about 100 due for delivery in 2025), 215 in earlier production.',
      },
    ],
  },
  {
    case_id: 'A330NEO-TOOL-2026',
    title: 'A330neo Stray Assembly Tool Inspection',
    event_date: null,
    public_statement_date: null,
    directive_date: null,
    directive_status: 'none_published_or_unknown',
    aircraft_affected_total: null,
    aircraft_in_service: null,
    aircraft_undelivered: null,
    deliveries_context:
      'Zero deliveries in June and July 2026; 3, 2, 4 in March, April, May; one on 11 Aug 2026; number of aircraft inspected not disclosed; policy to the regulator due mid-November 2026.',
    in_service_scope_notes:
      'Reports conflict: one says no retroactive fix is required for in-service aircraft, another says inspections are recommended for aircraft delivered from early 2021 to end of May 2026, with final requirements under discussion with the regulator. Needs verification.',
    days_event_to_statement: null,
    source_url: null,
    source_type: 'manufacturer',
    url_status: 'unchecked',
    verification_status: 'needs verification',
    sources: [
      {
        url: null,
        title: 'Airbus Monthly Orders & Deliveries Files (2026)',
        source_type: 'manufacturer',
        url_status: 'unchecked',
        fact_referenced: 'Official deliveries: March (3), April (2), May (4); June (0), July (0); 11 Aug 2026 (1).',
      },
      {
        url: null,
        title: 'Regulator Oversight Discussion',
        source_type: 'regulator',
        url_status: 'unchecked',
        fact_referenced: 'Inspection policy to the regulator due mid-November 2026; in-service requirements under discussion.',
      },
    ],
    dated_events: [
      {
        date: '2026-03-31',
        label: 'March Deliveries',
        description: '3 A330neo aircraft delivered.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2026-04-30',
        label: 'April Deliveries',
        description: '2 A330neo aircraft delivered.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2026-05-31',
        label: 'May Deliveries',
        description: '4 A330neo aircraft delivered (total 9 in March–May).',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2026-06-30',
        label: 'June Delivery Pause',
        description: 'Zero A330neo deliveries during assembly tool inspection pause.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2026-07-31',
        label: 'July Delivery Pause',
        description: 'Zero A330neo deliveries during continued tool inspection.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2026-08-11',
        label: 'Deliveries Resume',
        description: 'One A330neo delivered on 11 Aug 2026.',
        source_url: null,
        source_type: 'manufacturer',
        url_status: 'unchecked',
      },
      {
        date: '2026-11-15',
        label: 'Regulator Policy Filing Milestone',
        description: 'Inspection policy to the regulator due mid-November 2026.',
        source_url: null,
        source_type: 'regulator',
        url_status: 'unchecked',
      },
    ],
    fleet_breakdowns: [],
  },
]

export default function IncidentClockPage() {
  const [cases, setCases] = useState<IncidentCase[]>(DEFAULT_CASES)
  const [activePreset, setActivePreset] = useState<string | null>(null)
  const [sourcedFields, setSourcedFields] = useState<string[]>([])
  const [displayOnlyPublicGap, setDisplayOnlyPublicGap] = useState<number | null>(null)

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

  const hasUnverifiedSources = useMemo(() => {
    return (
      cases.length === 0 ||
      cases.some(
        (c) =>
          !c.source_url ||
          c.verification_status !== 'sourced' ||
          c.url_status !== 'verified by user' ||
          (c.dated_events && c.dated_events.some((e) => !e.source_url || e.url_status !== 'verified by user'))
      )
    )
  }, [cases])

  // Presets load ONLY sourced parameters; unsourced fields remain empty and visually highlighted
  const handleApplyPreset = (presetId: string) => {
    setActivePreset(presetId)
    if (presetId === 'A320-SOLAR-2025') {
      // Phase 7.2 rule: Remove days_to_scope = 29 from the preset.
      // Store it as a separate display-only field that cannot feed the calculator.
      // The preset leaves days_to_scope empty.
      setDaysToScope('')
      setInService('')
      setUndelivered('')
      setBaselineRate('')
      setShareRecovered('')
      setValuePerAircraft('')
      setSourcedFields([])
      setDisplayOnlyPublicGap(29)
    } else if (presetId === 'A320-PANEL-2025') {
      setDaysToScope('')
      setInService('177')
      setUndelivered('451')
      setBaselineRate('')
      setShareRecovered('')
      setValuePerAircraft('')
      setSourcedFields(['aircraft_held_in_service', 'aircraft_held_undelivered'])
      setDisplayOnlyPublicGap(null)
    } else if (presetId === 'A330NEO-TOOL-2026' || presetId === 'A330-TOOL-2026') {
      setDaysToScope('')
      setInService('')
      setUndelivered('')
      setBaselineRate('')
      setShareRecovered('')
      setValuePerAircraft('')
      setSourcedFields([])
      setDisplayOnlyPublicGap(null)
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
    setDisplayOnlyPublicGap(null)
  }

  // Parse numeric values
  const parsedDays = daysToScope.trim() !== '' ? parseFloat(daysToScope) : null
  const parsedInService = inService.trim() !== '' ? parseFloat(inService) : null
  const parsedUndelivered = undelivered.trim() !== '' ? parseFloat(undelivered) : null
  const parsedRate = baselineRate.trim() !== '' ? parseFloat(baselineRate) : null
  const parsedShare = shareRecovered.trim() !== '' ? parseFloat(shareRecovered) / 100.0 : null
  const parsedValue = valuePerAircraft.trim() !== '' ? parseFloat(valuePerAircraft) : null

  // Calculations (strict formula enforcement from Phase 7)
  const calcResults = useMemo(() => {
    const hasHeld = parsedInService !== null || parsedUndelivered !== null
    const totalHeld = hasHeld ? (parsedInService || 0) + (parsedUndelivered || 0) : null

    // a. Total Aircraft-Days Held = total held * days
    const aircraftDaysHeld = totalHeld !== null && parsedDays !== null ? totalHeld * parsedDays : null

    // b. Model A (Line Stop): gross = baseline_rate * (days / 30), net = gross * (1 - share_recovered)
    let modelAGross: number | null = null
    let modelANet: number | null = null
    if (parsedRate !== null && parsedDays !== null) {
      modelAGross = parsedRate * (parsedDays / 30.0)
      const rec = parsedShare !== null ? parsedShare : 0.0
      modelANet = modelAGross * (1.0 - rec)
    }

    // c. Model B (Hold of Finished Aircraft): handover delay in aircraft-days = undelivered * days
    let modelBAircraftDays: number | null = null
    if (parsedUndelivered !== null && parsedDays !== null) {
      modelBAircraftDays = parsedUndelivered * parsedDays
    } else if (totalHeld !== null && parsedDays !== null && parsedUndelivered === null) {
      modelBAircraftDays = totalHeld * parsedDays
    }

    // One-Day Cost of Delay (aircraft-days / day) = 1 day * total held
    const oneDayAircraftDays = totalHeld !== null ? totalHeld : null

    // Financial calculations: STRICTLY null if value_per_aircraft is blank
    let financialImpact: number | null = null
    let oneDayMoney: number | null = null
    if (parsedValue !== null) {
      if (modelANet !== null) {
        financialImpact = modelANet * parsedValue
      }
      if (parsedRate !== null) {
        const rec = parsedShare !== null ? parsedShare : 0.0
        const dailyNetLost = (parsedRate / 30.0) * (1.0 - rec)
        oneDayMoney = dailyNetLost * parsedValue
      }
    }

    // Sensitivity Matrix over duration multipliers: 0.5x, 1.0x, 2.0x
    const sensitivity = [0.5, 1.0, 2.0].map((mult) => {
      const d = parsedDays !== null ? parsedDays * mult : null
      const adh = totalHeld !== null && d !== null ? totalHeld * d : null
      let mANet: number | null = null
      if (parsedRate !== null && d !== null) {
        const gross = parsedRate * (d / 30.0)
        const rec = parsedShare !== null ? parsedShare : 0.0
        mANet = gross * (1.0 - rec)
      }
      let mB: number | null = null
      if (parsedUndelivered !== null && d !== null) {
        mB = parsedUndelivered * d
      } else if (totalHeld !== null && d !== null && parsedUndelivered === null) {
        mB = totalHeld * d
      }
      let fImpact: number | null = null
      if (parsedValue !== null && mANet !== null) {
        fImpact = mANet * parsedValue
      }
      return {
        multiplier: mult,
        days: d,
        aircraftDaysHeld: adh,
        modelANet: mANet,
        modelB: mB,
        financialImpact: fImpact,
      }
    })

    return {
      totalHeld,
      aircraftDaysHeld,
      modelAGross,
      modelANet,
      modelBAircraftDays,
      financialImpact,
      oneDayAircraftDays,
      oneDayMoney,
      sensitivity,
    }
  }, [parsedDays, parsedInService, parsedUndelivered, parsedRate, parsedShare, parsedValue])

  const formatMoney = (val: number | null): string => {
    if (val === null) return '--'
    if (val >= 1e9) {
      return `$${(val / 1e9).toFixed(2)} B`
    }
    if (val >= 1e6) {
      return `$${(val / 1e6).toFixed(2)} M`
    }
    return `$${val.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
  }

  const getSourceTypeBadge = (sourceType?: string | null) => {
    if (!sourceType) return null
    const map: Record<string, { bg: string; text: string; border: string; label: string }> = {
      regulator: { bg: 'rgba(56, 189, 248, 0.15)', text: '#38bdf8', border: '#0284c7', label: 'REGULATOR' },
      manufacturer: { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: '#9333ea', label: 'MANUFACTURER' },
      wire: { bg: 'rgba(251, 191, 36, 0.15)', text: '#fbbf24', border: '#d97706', label: 'NEWS WIRE' },
      media: { bg: 'rgba(148, 163, 184, 0.15)', text: '#cbd5e1', border: '#475569', label: 'MEDIA' },
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
      none_published_or_unknown: {
        bg: 'rgba(148, 163, 184, 0.15)',
        text: '#94a3b8',
        border: '#475569',
        label: 'NONE PUBLISHED / UNKNOWN',
      },
    }
    const conf = map[status] || map.none_published_or_unknown
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

  const getUrlStatusBadge = (status?: string | null) => {
    const isVerified = status === 'verified by user'
    return (
      <span
        data-testid={`badge-url-status-${status || 'unchecked'}`}
        style={{
          fontSize: '0.625rem',
          fontWeight: 600,
          padding: '2px 5px',
          borderRadius: '3px',
          backgroundColor: isVerified ? 'rgba(34, 197, 94, 0.15)' : 'rgba(100, 116, 139, 0.2)',
          color: isVerified ? '#4ade80' : '#94a3b8',
          border: `1px solid ${isVerified ? '#16a34a' : '#475569'}`,
          letterSpacing: '0.02em',
        }}
      >
        {status || 'unchecked'}
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

        {/* Phase 7.1/7.2 Mandatory Radiation Exposure Context Box */}
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
            <strong>Radiation Exposure Context &amp; Scope:</strong> Airbus stated that intense solar radiation may corrupt
            data critical to flight controls. Independent experts have questioned whether the radiation level on that
            date was unusual. Axis B is exposure context, not a cause.
          </p>
        </div>
      </div>

      {/* Phase 8.1 Work in Progress: Sources Being Verified Header */}
      {hasUnverifiedSources && (
        <aside
          role="region"
          aria-label="Source Verification Status"
          data-testid="sources-work-in-progress-header"
          style={{
            padding: '16px 20px',
            borderRadius: '8px',
            backgroundColor: 'rgba(180, 83, 9, 0.25)',
            border: '1px solid #f59e0b',
            display: 'flex',
            alignItems: 'center',
            gap: '14px',
            color: '#fef3c7',
          }}
        >
          <AlertTriangle size={24} style={{ color: '#fbbf24', flexShrink: 0 }} aria-hidden="true" />
          <div>
            <h3 style={{ margin: 0, fontSize: '0.9375rem', fontWeight: 700, color: '#fef3c7' }}>
              Work in progress: sources being verified
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: '0.8125rem', color: '#fde68a', lineHeight: 1.5 }}>
              One or more cases lack a verified primary regulatory URL. Red markers highlight unverified or missing primary documentation.
            </p>
          </div>
        </aside>
      )}

      {/* 2. Public Case Ground Truth Display */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc' }}>
            Public Incident Ground Truth Cases
          </h3>
          <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
            All cases tagged "needs verification" until URLs are user-confirmed.
          </span>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '16px',
          }}
        >
          {cases.map((c) => (
            <div
              key={c.case_id}
              className="glass-panel"
              data-testid={`case-card-${c.case_id}`}
              style={{
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderLeft: '4px solid #38bdf8',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <code style={{ fontSize: 'var(--text-xs)', color: '#38bdf8', fontWeight: 700 }}>{c.case_id}</code>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                    {getDirectiveStatusBadge(c.directive_status)}
                    <span
                      data-testid={`badge-verification-${c.case_id}`}
                      style={{
                        fontSize: '0.625rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        backgroundColor: c.verification_status === 'sourced' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)',
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
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <span style={{ color: '#94a3b8' }}>In-Service Scope:</span>
                      <span style={{ color: '#fbbf24', fontWeight: 600, fontSize: '0.6875rem', lineHeight: 1.4 }}>
                        {c.in_service_scope_notes}
                      </span>
                    </div>
                  )}
                  {c.days_event_to_statement !== null && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Event-to-Statement Gap:</span>
                      <span style={{ color: '#38bdf8', fontWeight: 700 }}>{c.days_event_to_statement} days</span>
                    </div>
                  )}
                  {c.deliveries_context && (
                    <p style={{ margin: '6px 0 0', fontSize: '0.6875rem', color: '#94a3b8', fontStyle: 'italic', lineHeight: 1.4 }}>
                      {c.deliveries_context}
                    </p>
                  )}
                </div>

                {/* Sourced Fleet Breakdowns */}
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
                            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                              {getSourceTypeBadge(b.source_type)}
                              {getUrlStatusBadge(b.url_status)}
                            </div>
                          </div>
                          {b.notes && (
                            <div style={{ fontSize: '0.75rem', color: '#e2e8f0', marginTop: '2px', fontWeight: 500 }}>
                              {b.notes}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Dated Events Milestone List */}
                {c.dated_events && c.dated_events.length > 0 && (
                  <div style={{ marginTop: '12px', borderTop: '1px solid #1e293b', paddingTop: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                      <Calendar size={13} style={{ color: '#38bdf8' }} aria-hidden="true" />
                      <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                        Dated Chronology
                      </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
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
                            {getUrlStatusBadge(evt.url_status)}
                          </div>
                          <span style={{ color: '#cbd5e1', fontSize: '0.6875rem' }}>{evt.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Sourced URLs Section */}
              <div style={{ borderTop: '1px solid #1e293b', paddingTop: '10px', marginTop: '12px' }}>
                <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#94a3b8', marginBottom: '6px' }}>
                  REGULATORY &amp; PRIMARY SOURCES
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {c.sources && c.sources.length > 0 ? (
                    c.sources.map((src, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px' }}>
                        {src.url ? (
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
                        ) : (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span style={{ fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>{src.title}</span>
                            <span style={{ color: '#ef4444', fontWeight: 600, fontSize: 'var(--text-xs)' }}>
                              primary source missing
                            </span>
                          </div>
                        )}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {getSourceTypeBadge(src.source_type)}
                          {getUrlStatusBadge(src.url_status)}
                        </div>
                      </div>
                    ))
                  ) : null}

                  {/* Primary URL display rule */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '4px' }}>
                    <span style={{ color: '#94a3b8', fontSize: 'var(--text-xs)' }}>Primary Document:</span>
                    {c.source_url ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
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
                          <span>Primary Link</span>
                          <ExternalLink size={11} aria-hidden="true" />
                        </a>
                        {getUrlStatusBadge(c.url_status)}
                      </div>
                    ) : (
                      <span
                        data-testid={`primary-source-missing-${c.case_id}`}
                        style={{ color: '#ef4444', fontWeight: 600, fontSize: 'var(--text-xs)' }}
                      >
                        primary source missing
                      </span>
                    )}
                  </div>
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
              Preset: A320 Solar (Public Gap 29d)
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

        {/* Phase 7.2 Separate Display-Only Field for Public Gap */}
        {displayOnlyPublicGap !== null && (
          <div
            data-testid="public-statement-gap-callout"
            style={{
              padding: '12px 16px',
              borderRadius: '6px',
              backgroundColor: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.35)',
              marginBottom: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#38bdf8' }}>
                Separate Display-Only Field: days_event_to_public_statement = {displayOnlyPublicGap} Days
              </span>
              <span
                style={{
                  fontSize: '0.6875rem',
                  padding: '1px 6px',
                  borderRadius: '4px',
                  backgroundColor: 'rgba(239, 68, 68, 0.15)',
                  color: '#fca5a5',
                  border: '1px solid #ef4444',
                  fontWeight: 600,
                }}
              >
                Does Not Feed Calculator
              </span>
            </div>
            <p style={{ margin: 0, fontSize: 'var(--text-xs)', color: '#cbd5e1', lineHeight: 1.5 }}>
              This is the public gap between the incident and Airbus's statement. It is not a hold period and not a scoping time.
            </p>
          </div>
        )}

        {/* Inputs Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {/* 1. Days to Scope */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-days-to-scope" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Days to Scope
              </label>
              {sourcedFields.includes('days_to_scope') ? (
                <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>
                  SOURCED
                </span>
              ) : (
                <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                  SCENARIO / UNVERIFIED
                </span>
              )}
            </div>
            <input
              id="input-days-to-scope"
              data-testid="input-days-to-scope"
              type="number"
              placeholder="e.g. 30"
              value={daysToScope}
              onChange={(e) => setDaysToScope(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: sourcedFields.includes('days_to_scope') ? '1px solid #22c55e' : '1px solid #475569',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
              Duration required to identify and isolate affected aircraft.
            </span>
          </div>

          {/* 2. Aircraft Held In-Service */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-in-service" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Aircraft Held In-Service
              </label>
              {sourcedFields.includes('aircraft_held_in_service') ? (
                <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>
                  SOURCED
                </span>
              ) : (
                <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                  SCENARIO / UNVERIFIED
                </span>
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
                padding: '8px 12px',
                borderRadius: '6px',
                border: sourcedFields.includes('aircraft_held_in_service') ? '1px solid #22c55e' : '1px solid #475569',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
              Delivered aircraft requiring operational hold or inspection.
            </span>
          </div>

          {/* 3. Aircraft Held Undelivered */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-undelivered" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Aircraft Held Undelivered
              </label>
              {sourcedFields.includes('aircraft_held_undelivered') ? (
                <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>
                  SOURCED
                </span>
              ) : (
                <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                  SCENARIO / UNVERIFIED
                </span>
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
                padding: '8px 12px',
                borderRadius: '6px',
                border: sourcedFields.includes('aircraft_held_undelivered') ? '1px solid #22c55e' : '1px solid #475569',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
              Finished aircraft paused at delivery center or FAL.
            </span>
          </div>

          {/* 4. Baseline Monthly Handover Rate */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-baseline-rate" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Baseline Handover Rate / Month
              </label>
              <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                USER INPUT (OPTIONAL)
              </span>
            </div>
            <input
              id="input-baseline-rate"
              data-testid="input-baseline-rate"
              type="number"
              placeholder="e.g. 60 (Model A)"
              value={baselineRate}
              onChange={(e) => setBaselineRate(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #475569',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
              Normal monthly output required for Model A line-stop impact.
            </span>
          </div>

          {/* 5. Share Recovered Later (%) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-share-recovered" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Share Recovered Later (%)
              </label>
              <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                USER INPUT (OPTIONAL)
              </span>
            </div>
            <input
              id="input-share-recovered"
              data-testid="input-share-recovered"
              type="number"
              placeholder="e.g. 20 (Model A Net)"
              value={shareRecovered}
              onChange={(e) => setShareRecovered(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #475569',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
              Percentage of delayed handovers caught up in later quarters.
            </span>
          </div>

          {/* 6. Value per Aircraft ($) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="input-value-per-aircraft" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#f8fafc' }}>
                Value per Aircraft ($)
              </label>
              <span style={{ fontSize: '0.625rem', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                NO DEFAULT (LEAVE BLANK FOR NO $)
              </span>
            </div>
            <input
              id="input-value-per-aircraft"
              data-testid="input-value-per-aircraft"
              type="number"
              placeholder="Leave blank for no money figure"
              value={valuePerAircraft}
              onChange={(e) => setValuePerAircraft(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #475569',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: '#f8fafc',
                fontSize: 'var(--text-sm)',
              }}
            />
            <span style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
              Net delivery value. If blank, no financial figures appear anywhere.
            </span>
          </div>
        </div>

        {/* 5. Four Core Outputs Display */}
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ margin: '0 0 12px', fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc' }}>
            Modelled Scoping Consequences
          </h4>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '16px',
            }}
          >
            {/* Output a: Total Aircraft-Days Held */}
            <div
              className="glass-panel"
              data-testid="card-aircraft-days-held"
              style={{
                padding: '16px',
                borderLeft: '4px solid #38bdf8',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <Layers size={16} style={{ color: '#38bdf8' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                  Output a: Fleet Holding Exposure
                </span>
              </div>
              <div
                data-testid="val-aircraft-days-held"
                style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', margin: '4px 0' }}
              >
                {calcResults.aircraftDaysHeld !== null ? calcResults.aircraftDaysHeld.toLocaleString() : '--'}
              </div>
              <span style={{ fontSize: 'var(--text-xs)', color: '#38bdf8' }}>Aircraft-Days Held</span>
              <p style={{ margin: '8px 0 0', fontSize: '0.6875rem', color: '#94a3b8', lineHeight: 1.4 }}>
                Formula: (aircraft_held_in_service + aircraft_held_undelivered) × days_to_scope
              </p>
            </div>

            {/* Output b: Model A - Line Stop */}
            <div
              className="glass-panel"
              data-testid="card-model-a"
              style={{
                padding: '16px',
                borderLeft: '4px solid #f59e0b',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <TrendingDown size={16} style={{ color: '#fbbf24' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                  Output b: Model A (Line Stop)
                </span>
              </div>
              <div
                data-testid="val-model-a-net"
                style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', margin: '4px 0' }}
              >
                {calcResults.modelANet !== null ? calcResults.modelANet.toFixed(1) : '--'}
              </div>
              <span style={{ fontSize: 'var(--text-xs)', color: '#fbbf24' }}>
                Net Handovers Lost {calcResults.modelAGross !== null ? `(Gross: ${calcResults.modelAGross.toFixed(1)})` : ''}
              </span>
              <p style={{ margin: '8px 0 0', fontSize: '0.6875rem', color: '#94a3b8', lineHeight: 1.4 }}>
                Formula: baseline_rate × (days / 30) × (1 - share_recovered)
              </p>
            </div>

            {/* Output c: Model B - Finished Aircraft Hold */}
            <div
              className="glass-panel"
              data-testid="card-model-b"
              style={{
                padding: '16px',
                borderLeft: '4px solid #a855f7',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <Clock size={16} style={{ color: '#c084fc' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                  Output c: Model B (Finished Hold)
                </span>
              </div>
              <div
                data-testid="val-model-b-days"
                style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', margin: '4px 0' }}
              >
                {calcResults.modelBAircraftDays !== null ? calcResults.modelBAircraftDays.toLocaleString() : '--'}
              </div>
              <span style={{ fontSize: 'var(--text-xs)', color: '#c084fc' }}>Delivery Delay (Aircraft-Days)</span>
              <p style={{ margin: '8px 0 0', fontSize: '0.6875rem', color: '#94a3b8', lineHeight: 1.4 }}>
                Formula: aircraft_held_undelivered × days_to_scope (measured only in aircraft-days)
              </p>
            </div>

            {/* Output d: Valuation Impact */}
            <div
              className="glass-panel"
              data-testid="card-valuation-impact"
              style={{
                padding: '16px',
                borderLeft: '4px solid #10b981',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <DollarSign size={16} style={{ color: '#34d399' }} aria-hidden="true" />
                <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                  Output d: Valuation Impact
                </span>
              </div>
              <div
                data-testid="val-financial-impact"
                style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', margin: '4px 0' }}
              >
                {formatMoney(calcResults.financialImpact)}
              </div>
              <span style={{ fontSize: 'var(--text-xs)', color: '#34d399' }}>
                {calcResults.financialImpact !== null ? 'Model A Financial Slippage' : 'No value per aircraft entered'}
              </span>
              <p style={{ margin: '8px 0 0', fontSize: '0.6875rem', color: '#94a3b8', lineHeight: 1.4 }}>
                If value is blank, no money figure is shown (Phase 7 rule).
              </p>
            </div>
          </div>
        </div>

        {/* 6. One-Day Cost of Delay Callout */}
        <div
          data-testid="panel-one-day-cost"
          style={{
            padding: '16px 20px',
            borderRadius: '8px',
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid #334155',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
            marginBottom: '24px',
          }}
        >
          <div>
            <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
              One-Day Cost of Delay
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginTop: '2px' }}>
              <span
                data-testid="val-one-day-aircraft-days"
                style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}
              >
                {calcResults.oneDayAircraftDays !== null
                  ? `${calcResults.oneDayAircraftDays.toLocaleString()} aircraft-days / day`
                  : '--'}
              </span>
              <span
                data-testid="val-one-day-money"
                style={{ fontSize: 'var(--text-sm)', color: '#94a3b8', fontWeight: 600 }}
              >
                {calcResults.oneDayMoney !== null
                  ? `(${formatMoney(calcResults.oneDayMoney)} / day net line loss)`
                  : '(No money figure: value per aircraft blank)'}
              </span>
            </div>
          </div>
          <span style={{ fontSize: 'var(--text-xs)', color: '#94a3b8', maxWidth: '380px', textAlign: 'right' }}>
            Marginal operational holding exposure added for every additional day spent scoping before containment.
          </span>
        </div>

        {/* 7. Sensitivity Matrix (0.5x, 1.0x, 2.0x) */}
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ margin: '0 0 10px', fontSize: 'var(--text-base)', fontWeight: 700, color: '#f8fafc' }}>
            Duration Sensitivity Matrix
          </h4>
          <p style={{ margin: '0 0 14px', fontSize: 'var(--text-xs)', color: '#94a3b8' }}>
            Evaluating scoping duration impacts at 0.5x, 1.0x, and 2.0x of the entered baseline duration.
          </p>

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
                <tr style={{ borderBottom: '2px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '8px 12px' }}>Multiplier</th>
                  <th style={{ padding: '8px 12px' }}>Scoping Duration</th>
                  <th style={{ padding: '8px 12px' }}>Output a: Aircraft-Days Held</th>
                  <th style={{ padding: '8px 12px' }}>Output b: Model A Net Lost</th>
                  <th style={{ padding: '8px 12px' }}>Output c: Model B Delay (Aircraft-Days)</th>
                  <th style={{ padding: '8px 12px' }}>Output d: Financial Impact</th>
                </tr>
              </thead>
              <tbody>
                {calcResults.sensitivity.map((row) => (
                  <tr
                    key={row.multiplier}
                    style={{
                      borderBottom: '1px solid #1e293b',
                      backgroundColor: row.multiplier === 1.0 ? 'rgba(56, 189, 248, 0.08)' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '10px 12px', fontWeight: 700, color: '#38bdf8' }}>
                      {row.multiplier.toFixed(1)}x {row.multiplier === 1.0 ? '(Base)' : ''}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#f8fafc' }}>
                      {row.days !== null ? `${row.days.toFixed(1)} days` : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#f8fafc' }}>
                      {row.aircraftDaysHeld !== null ? row.aircraftDaysHeld.toLocaleString() : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#fbbf24' }}>
                      {row.modelANet !== null ? row.modelANet.toFixed(1) : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#c084fc' }}>
                      {row.modelB !== null ? row.modelB.toLocaleString() : '--'}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#34d399', fontWeight: 600 }}>
                      {formatMoney(row.financialImpact)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 8. Disclosed Formulas and Engineering Assumptions */}
        <div style={{ borderTop: '1px solid #334155', paddingTop: '16px' }}>
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
            Transparent Formulas &amp; Scenario Assumptions
          </span>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '12px',
              marginTop: '8px',
            }}
          >
            <div style={{ padding: '10px 12px', borderRadius: '4px', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '0.6875rem', color: '#38bdf8', fontWeight: 700 }}>Formula a (Aircraft-Days Held)</div>
              <code style={{ fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
                aircraft_days_held = (in_service + undelivered) × days_to_scope
              </code>
            </div>

            <div style={{ padding: '10px 12px', borderRadius: '4px', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '0.6875rem', color: '#fbbf24', fontWeight: 700 }}>Formula b (Model A Net Lost)</div>
              <code style={{ fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
                rate × (days / 30) × (1 - share_recovered)
              </code>
            </div>

            <div style={{ padding: '10px 12px', borderRadius: '4px', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '0.6875rem', color: '#c084fc', fontWeight: 700 }}>Formula c (Model B Delay)</div>
              <code style={{ fontSize: 'var(--text-xs)', color: '#cbd5e1' }}>
                handover_delay_aircraft_days = aircraft_held_undelivered × days_to_scope
              </code>
            </div>
          </div>

          <ul style={{ margin: '12px 0 0', paddingLeft: '18px', fontSize: '0.6875rem', color: '#94a3b8', lineHeight: 1.5 }}>
            <li>Held aircraft count is assumed uniform across the scoping duration.</li>
            <li>Model A assumes uniform monthly delivery rate across standard 30-day calendar months.</li>
            <li>Model B measures holding duration of finished aircraft exclusively in aircraft-days.</li>
            <li>Financial impact is completely withheld unless value per aircraft is explicitly specified.</li>
            <li>Scenario calculations reflect user inputs and public disclosures only, not internal manufacturer records.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
