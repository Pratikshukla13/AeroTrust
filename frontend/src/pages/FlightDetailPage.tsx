import { useEffect, useState } from 'react'
import { Sun } from 'lucide-react'

interface CheckInfo {
  name: string
  label: string
  role: string
  flag: boolean
  reasons: string[]
  residual?: number | null
  note?: string | null
}

interface RadiationInfo {
  tier: string
  label: string
  relative_index?: number | null
  notice: string
}

interface FlightPoint {
  ts: number
  baro_alt_m: number
  geo_alt_m: number
  residual_m: number
  is_flagged: boolean
}

interface FlightDetailData {
  flight_id: string
  icao24: string
  tier: string
  tier_reasons: string[]
  check_a: CheckInfo
  check_b: CheckInfo
  check_c: CheckInfo
  check_d: CheckInfo
  radiation: RadiationInfo
  uncalibrated_score?: number | null
  flagged_window?: { start_ts: number; end_ts: number } | null
  points: FlightPoint[]
}

interface FlightOption {
  flight_id: string
  icao24: string
  tier: string
}

export default function FlightDetailPage() {
  const [flightsList, setFlightsList] = useState<FlightOption[]>([])
  const [selectedFlightId, setSelectedFlightId] = useState<string>('x1007f8_1793875401')
  const [flightData, setFlightData] = useState<FlightDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 1. Fetch flight choices on mount
  useEffect(() => {
    fetch('/api/flights?limit=25')
      .then((res) => res.json())
      .then((data: FlightOption[]) => {
        if (data && data.length > 0) {
          setFlightsList(data)
          // Default to flagged flight if present in listing, else first
          const flagged = data.find((f) => f.tier === 'flagged_altitude_inconsistency')
          if (flagged) {
            setSelectedFlightId(flagged.flight_id)
          } else {
            setSelectedFlightId(data[0].flight_id)
          }
        }
      })
      .catch(() => {
        // Fallback to initial ID
      })
  }, [])

  // 2. Fetch specific flight telemetry detail
  useEffect(() => {
    if (!selectedFlightId) return
    setLoading(true)
    setError(null)

    fetch(`/api/flight-detail/${selectedFlightId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`)
        return res.json()
      })
      .then((json: FlightDetailData) => {
        setFlightData(json)
        setLoading(false)
      })
      .catch((err) => {
        setError(`Failed to retrieve flight telemetry: ${err.message}`)
        setLoading(false)
      })
  }, [selectedFlightId])

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'flagged_altitude_inconsistency':
        return { text: '#fb7185', bg: 'rgba(244, 63, 94, 0.12)', border: 'rgba(244, 63, 94, 0.4)' }
      case 'jamming_degraded':
        return { text: '#fbbf24', bg: 'rgba(251, 191, 36, 0.12)', border: 'rgba(251, 191, 36, 0.4)' }
      case 'insufficient':
        return { text: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', border: 'rgba(168, 85, 247, 0.4)' }
      case 'no_alert':
      default:
        return { text: '#34d399', bg: 'rgba(52, 211, 153, 0.12)', border: 'rgba(52, 211, 153, 0.4)' }
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Flight Selector Bar */}
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
              Flight Telemetry &amp; Detector Inspection
            </h2>
            <p style={{ margin: '4px 0 0', fontSize: '0.8125rem', color: '#94a3b8' }}>
              Single-flight telemetry: Check (a) primary altitude discrepancy, supporting checks, inactive consensus, and relative radiation tier.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <label htmlFor="flight-select" style={{ fontSize: '0.8125rem', color: '#cbd5e1', fontWeight: 600 }}>
              Inspected Flight:
            </label>
            <select
              id="flight-select"
              data-testid="flight-selector-dropdown"
              value={selectedFlightId}
              onChange={(e) => setSelectedFlightId(e.target.value)}
              style={{
                padding: '8px 12px',
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                border: '1px solid #475569',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: '0.8125rem',
                fontFamily: 'monospace',
                cursor: 'pointer',
              }}
            >
              {flightsList.map((fl) => (
                <option key={fl.flight_id} value={fl.flight_id}>
                  {fl.flight_id} [{fl.tier}]
                </option>
              ))}
              {flightsList.length === 0 && (
                <option value="x1007f8_1793875401">x1007f8_1793875401 [flagged_altitude_inconsistency]</option>
              )}
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <p style={{ margin: 0, color: '#38bdf8', fontSize: '0.9375rem' }}>Loading flight telemetry points...</p>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ padding: '24px', borderLeft: '4px solid #ef4444' }}>
          <p style={{ margin: 0, color: '#fca5a5', fontSize: '0.875rem' }}>{error}</p>
        </div>
      )}

      {!loading && flightData && (
        <>
          {/* Top KPI Summary Card: Tier, uncalibrated_score, Radiation Tier */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '20px',
              borderTop: `4px solid ${getTierColor(flightData.tier).text}`,
            }}
          >
            {/* Operational Tier */}
            <div>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>
                Evidence Tier
              </span>
              <div style={{ marginTop: '8px' }}>
                <span
                  data-testid="flight-tier-badge"
                  style={{
                    display: 'inline-block',
                    fontSize: '0.9375rem',
                    fontWeight: 700,
                    fontFamily: 'monospace',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    color: getTierColor(flightData.tier).text,
                    backgroundColor: getTierColor(flightData.tier).bg,
                    border: `1px solid ${getTierColor(flightData.tier).border}`,
                  }}
                >
                  {flightData.tier}
                </span>
              </div>
              <p style={{ margin: '8px 0 0', fontSize: '0.75rem', color: '#cbd5e1' }}>
                Assigned strictly from v0.3 operational tier nomenclature.
              </p>
            </div>

            {/* uncalibrated_score (Permitted ONLY on this page) */}
            <div data-testid="uncalibrated-score-container">
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>
                Uncalibrated Score
              </span>
              <div style={{ marginTop: '6px', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <span
                  data-testid="uncalibrated_score"
                  style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em', fontFamily: 'monospace' }}
                >
                  {flightData.uncalibrated_score !== null && flightData.uncalibrated_score !== undefined
                    ? flightData.uncalibrated_score.toFixed(4)
                    : 'N/A'}
                </span>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  label: <strong style={{ color: '#cbd5e1' }}>uncalibrated_score</strong>
                </span>
              </div>
              <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
                Raw evidence score prior to calibration. Calibrated likelihood is withheld on Axis A.
              </p>
            </div>

            {/* Radiation Tier (illustrative placeholder) */}
            <div data-testid="radiation-exposure-container">
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>
                Natural Radiation Exposure
              </span>
              <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sun size={18} style={{ color: '#fbbf24' }} aria-hidden="true" />
                <span style={{ fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc', textTransform: 'capitalize' }}>
                  {flightData.radiation.tier}
                </span>
                <span
                  style={{
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'rgba(251, 191, 36, 0.15)',
                    border: '1px solid rgba(251, 191, 36, 0.4)',
                    color: '#fbbf24',
                  }}
                >
                  {flightData.radiation.label}
                </span>
              </div>
              <p style={{ margin: '8px 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
                Relative Index: {flightData.radiation.relative_index ?? 1.0} &bull; {flightData.radiation.notice}
              </p>
            </div>
          </div>

          {/* 4 Checks Grid: Check (a) primary, (b) supporting, (c) supporting, (d) inactive */}
          <div>
            <h3 style={{ margin: '0 0 14px', fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
              Integrity Checks &amp; Detector Breakdown
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {/* Check a: Primary */}
              <div
                data-testid="check-a-card"
                className="glass-card"
                style={{
                  padding: '18px',
                  borderTop: `3px solid ${flightData.check_a.flag ? '#fb7185' : '#34d399'}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8' }}>Check (a) &bull; PRIMARY</span>
                  <span
                    style={{
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: flightData.check_a.flag ? '#991b1b' : 'rgba(52, 211, 153, 0.2)',
                      color: flightData.check_a.flag ? '#fee2e2' : '#34d399',
                    }}
                  >
                    {flightData.check_a.flag ? 'FLAGGED' : 'NOMINAL'}
                  </span>
                </div>
                <h4 style={{ margin: '0 0 6px', fontSize: '0.9375rem', color: '#f8fafc', fontWeight: 700 }}>
                  {flightData.check_a.label}
                </h4>
                <div style={{ fontSize: '0.8125rem', color: '#cbd5e1', marginBottom: '8px' }}>
                  Max Residual: <strong>{flightData.check_a.residual ? `${flightData.check_a.residual.toFixed(1)} m` : 'N/A'}</strong> (threshold: 120.0 m)
                </div>
                {flightData.check_a.reasons.length > 0 ? (
                  <div style={{ fontSize: '0.75rem', color: '#fb7185', fontFamily: 'monospace' }}>
                    {flightData.check_a.reasons.map((r, i) => (
                      <div key={i}>&bull; {r}</div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Within nominal tolerance bounds</div>
                )}
              </div>

              {/* Check b: Supporting Only */}
              <div
                data-testid="check-b-card"
                className="glass-card"
                style={{
                  padding: '18px',
                  borderTop: '3px solid #64748b',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8' }}>Check (b) &bull; SUPPORTING ONLY</span>
                  <span
                    style={{
                      fontSize: '0.6875rem',
                      fontWeight: 600,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(100, 116, 139, 0.2)',
                      color: '#cbd5e1',
                    }}
                  >
                    SUPPORTING ONLY
                  </span>
                </div>
                <h4 style={{ margin: '0 0 6px', fontSize: '0.9375rem', color: '#f8fafc', fontWeight: 700 }}>
                  {flightData.check_b.label}
                </h4>
                <div style={{ fontSize: '0.8125rem', color: '#cbd5e1', marginBottom: '8px' }}>
                  Residual: {flightData.check_b.residual ? `${flightData.check_b.residual.toFixed(3)} m/s²` : 'N/A'}
                </div>
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
                  Does not trigger alerts independently; provides secondary corroboration.
                </p>
              </div>

              {/* Check c: Supporting Only */}
              <div
                data-testid="check-c-card"
                className="glass-card"
                style={{
                  padding: '18px',
                  borderTop: '3px solid #64748b',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8' }}>Check (c) &bull; SUPPORTING ONLY</span>
                  <span
                    style={{
                      fontSize: '0.6875rem',
                      fontWeight: 600,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(100, 116, 139, 0.2)',
                      color: '#cbd5e1',
                    }}
                  >
                    SUPPORTING ONLY
                  </span>
                </div>
                <h4 style={{ margin: '0 0 6px', fontSize: '0.9375rem', color: '#f8fafc', fontWeight: 700 }}>
                  {flightData.check_c.label}
                </h4>
                <div style={{ fontSize: '0.8125rem', color: '#cbd5e1', marginBottom: '8px' }}>
                  Residual: {flightData.check_c.residual ? `${flightData.check_c.residual.toFixed(1)} m` : 'N/A'}
                </div>
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
                  Position-velocity vector drift check; supporting role only.
                </p>
              </div>

              {/* Check d: Inactive */}
              <div
                data-testid="check-d-card"
                className="glass-card"
                style={{
                  padding: '18px',
                  borderTop: '3px solid #ef4444',
                  backgroundColor: 'rgba(239, 68, 68, 0.05)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f87171' }}>Check (d) &bull; INACTIVE</span>
                  <span
                    style={{
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      backgroundColor: '#991b1b',
                      color: '#fee2e2',
                      border: '1px solid #dc2626',
                    }}
                  >
                    INACTIVE
                  </span>
                </div>
                <h4 style={{ margin: '0 0 6px', fontSize: '0.9375rem', color: '#f8fafc', fontWeight: 700 }}>
                  {flightData.check_d.label}
                </h4>
                <p style={{ margin: '6px 0 0', fontSize: '0.75rem', color: '#cbd5e1', lineHeight: 1.45 }}>
                  {flightData.check_d.note}
                </p>
              </div>
            </div>
          </div>

          {/* Altitude Plot: Barometric vs Geometric Altimetry with Flagged Window Highlight */}
          <div className="glass-panel" data-testid="altitude-plot-panel" style={{ padding: '24px 28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div>
                <h3 style={{ margin: '0 0 4px', fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
                  Geometric vs Barometric Altitude Telemetry Profile
                </h3>
                <p style={{ margin: 0, fontSize: '0.8125rem', color: '#94a3b8' }}>
                  Continuous trajectory altitude points with flagged discrepancy interval highlighted (|Geo - Baro| &gt; 120.0 m).
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '12px', height: '3px', backgroundColor: '#38bdf8' }} />
                  <span style={{ color: '#cbd5e1' }}>Barometric Alt (m)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '12px', height: '3px', backgroundColor: '#e879f9' }} />
                  <span style={{ color: '#cbd5e1' }}>Geometric Alt (m)</span>
                </div>
                {flightData.flagged_window && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '12px', height: '10px', backgroundColor: 'rgba(244, 63, 94, 0.3)', border: '1px solid #fb7185' }} />
                    <span style={{ color: '#fb7185', fontWeight: 600 }}>Flagged Window</span>
                  </div>
                )}
              </div>
            </div>

            {/* SVG Plot */}
            <div style={{ width: '100%', overflowX: 'auto', backgroundColor: '#070b14', borderRadius: '8px', padding: '16px', border: '1px solid #1e293b' }}>
              <AltitudePlot points={flightData.points} flaggedWindow={flightData.flagged_window} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function AltitudePlot({
  points,
  flaggedWindow,
}: {
  points: FlightPoint[]
  flaggedWindow?: { start_ts: number; end_ts: number } | null
}) {
  if (!points || points.length === 0) {
    return <div style={{ color: '#94a3b8', padding: '20px', textAlign: 'center' }}>No altitude points available for this track.</div>
  }

  const width = 960
  const height = 280
  const padLeft = 60
  const padRight = 30
  const padTop = 20
  const padBottom = 30

  const plotW = width - padLeft - padRight
  const plotH = height - padTop - padBottom

  const minTs = points[0].ts
  const maxTs = points[points.length - 1].ts
  const tsSpan = Math.max(1, maxTs - minTs)

  let minAlt = Infinity
  let maxAlt = -Infinity
  for (const p of points) {
    if (p.baro_alt_m < minAlt) minAlt = p.baro_alt_m
    if (p.baro_alt_m > maxAlt) maxAlt = p.baro_alt_m
    if (p.geo_alt_m < minAlt) minAlt = p.geo_alt_m
    if (p.geo_alt_m > maxAlt) maxAlt = p.geo_alt_m
  }
  const altSpan = Math.max(100, maxAlt - minAlt)

  const getX = (ts: number) => padLeft + ((ts - minTs) / tsSpan) * plotW
  const getY = (alt: number) => padTop + plotH - ((alt - minAlt) / altSpan) * plotH

  // Generate SVG paths
  const baroPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.ts).toFixed(1)} ${getY(p.baro_alt_m).toFixed(1)}`).join(' ')
  const geoPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.ts).toFixed(1)} ${getY(p.geo_alt_m).toFixed(1)}`).join(' ')

  // Flagged window coordinates
  let winX1 = 0
  let winW = 0
  if (flaggedWindow) {
    winX1 = getX(flaggedWindow.start_ts)
    const winX2 = getX(flaggedWindow.end_ts)
    winW = Math.max(10, winX2 - winX1)
  }

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      style={{ width: '100%', minWidth: '700px', height: 'auto', display: 'block' }}
      role="img"
      aria-label="Geometric versus Barometric Altitude Telemetry Plot"
    >
      {/* Background grid */}
      {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
        const y = padTop + plotH * ratio
        const altVal = Math.round(maxAlt - ratio * altSpan)
        return (
          <g key={ratio}>
            <line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="#1e293b" strokeDasharray="3 3" />
            <text x={padLeft - 8} y={y + 4} fill="#64748b" fontSize="10" textAnchor="end" fontFamily="monospace">
              {altVal}m
            </text>
          </g>
        )
      })}

      {/* Flagged window highlight band */}
      {flaggedWindow && winW > 0 && (
        <rect
          x={winX1}
          y={padTop}
          width={winW}
          height={plotH}
          fill="rgba(244, 63, 94, 0.18)"
          stroke="#f43f5e"
          strokeWidth="1.5"
          strokeDasharray="4 2"
        />
      )}

      {/* Trajectory Lines */}
      <path d={baroPath} fill="none" stroke="#38bdf8" strokeWidth="2.5" />
      <path d={geoPath} fill="none" stroke="#e879f9" strokeWidth="2" strokeDasharray="5 3" />

      {/* X Axis Time Marks */}
      {[0, 0.5, 1].map((ratio) => {
        const x = padLeft + plotW * ratio
        const minVal = Math.round((ratio * tsSpan) / 60)
        return (
          <text key={ratio} x={x} y={height - 8} fill="#64748b" fontSize="10" textAnchor="middle" fontFamily="monospace">
            +{minVal} min
          </text>
        )
      })}
    </svg>
  )
}
