import { useEffect, useState } from 'react'
import { AlertOctagon } from 'lucide-react'

interface BaseRateRow {
  scenario: string
  prevalence_pct: number
  precision_pct: number
  ci_low: number
  ci_high: number
  false_alarms_per_10k: number
  guidance: string
}

interface LimitationsData {
  tag: string
  dataset_fingerprint: {
    tag: string
    name: string
    seed: string
    flights: number
    primary_unit: string
    config_hash: string
  }
  bullets: string[]
  base_rate_table: BaseRateRow[]
}

export default function LimitationsPage() {
  const [data, setData] = useState<LimitationsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/limitations')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`)
        return res.json()
      })
      .then((json: LimitationsData) => {
        setData(json)
        setLoading(false)
      })
      .catch((err) => {
        setError(`Failed to retrieve limitations: ${err.message}`)
        setLoading(false)
      })
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Panel */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <div style={{ padding: '6px', borderRadius: '6px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>
            <AlertOctagon size={20} aria-hidden="true" />
          </div>
          <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>
            Methodology &amp; Engineering Limitations
          </h1>
        </div>
        <p style={{ margin: 0, fontSize: '0.875rem', color: '#94a3b8', lineHeight: 1.6 }}>
          Comprehensive engineering boundaries, noise assumptions, abstention scope, and threat base-rate sensitivity disclosures.
        </p>
      </div>

      {loading && (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <p style={{ margin: 0, color: '#38bdf8', fontSize: '0.9375rem' }}>Loading limitations from API...</p>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ padding: '24px', borderLeft: '4px solid #ef4444' }}>
          <p style={{ margin: 0, color: '#fca5a5', fontSize: '0.875rem' }}>{error}</p>
        </div>
      )}

      {!loading && data && (
        <>
          {/* Engineering Boundary Disclosures (8 Core Bullets) */}
          <div className="glass-panel" data-testid="limitations-bullets-panel" style={{ padding: '24px 28px' }}>
            <h2 style={{ margin: '0 0 16px', fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
              Operational Boundaries &amp; Caveats
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {data.bullets.map((bullet, idx) => {
                const parts = bullet.split(':')
                const title = parts[0]
                const desc = parts.slice(1).join(':')

                return (
                  <div
                    key={idx}
                    data-testid={`limitation-item-${idx}`}
                    style={{
                      padding: '14px 18px',
                      backgroundColor: 'rgba(30, 41, 59, 0.5)',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                      display: 'flex',
                      gap: '12px',
                      alignItems: 'flex-start',
                    }}
                  >
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(56, 189, 248, 0.15)',
                        color: '#38bdf8',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        flexShrink: 0,
                        marginTop: '2px',
                      }}
                    >
                      {idx + 1}
                    </span>
                    <div>
                      <h3 style={{ margin: '0 0 4px', fontSize: '0.9375rem', fontWeight: 700, color: '#f8fafc' }}>
                        {title}
                      </h3>
                      <p style={{ margin: 0, fontSize: '0.8125rem', color: '#cbd5e1', lineHeight: 1.55 }}>
                        {desc.trim()}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Base-Rate Table: Expected Precision vs Threat Prevalence */}
          <div className="glass-panel" data-testid="base-rate-table-panel" style={{ padding: '24px 28px', overflowX: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
                  Threat Base-Rate &amp; Precision Sensitivity Table
                </h2>
                <p style={{ margin: 0, fontSize: '0.8125rem', color: '#94a3b8' }}>
                  Demonstrating that detector precision drops sharply in peacetime environments due to the false alarm base rate (Bayes rule).
                </p>
              </div>

              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: 'rgba(239, 68, 68, 0.12)',
                  border: '1px solid rgba(239, 68, 68, 0.35)',
                  color: '#f87171',
                  fontWeight: 600,
                }}
              >
                Bayesian Base-Rate Reality
              </span>
            </div>

            <table
              data-testid="base-rate-table"
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: '0.8125rem',
                textAlign: 'left',
              }}
            >
              <thead>
                <tr style={{ borderBottom: '2px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>Airspace Operational Scenario</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>Threat Prevalence (p)</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>Expected Precision</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'center' }}>95% Wilson Bounds</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>False Alarms / 10k Flights</th>
                  <th style={{ padding: '10px 12px', fontWeight: 700 }}>Operational Alerting Guidance</th>
                </tr>
              </thead>
              <tbody>
                {data.base_rate_table.map((row, idx) => {
                  const isLowPrec = row.precision_pct < 10.0
                  return (
                    <tr
                      key={idx}
                      data-testid={`base-rate-row-${idx}`}
                      style={{
                        borderBottom: '1px solid #1e293b',
                        backgroundColor: isLowPrec ? 'rgba(239, 68, 68, 0.05)' : 'rgba(30, 41, 59, 0.4)',
                      }}
                    >
                      <td style={{ padding: '12px', fontWeight: 700, color: '#f8fafc' }}>
                        {row.scenario}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontFamily: 'monospace', color: '#cbd5e1' }}>
                        {row.prevalence_pct.toFixed(2)}%
                      </td>
                      <td
                        style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontFamily: 'monospace',
                          fontWeight: 700,
                          color: isLowPrec ? '#f87171' : '#34d399',
                        }}
                      >
                        {row.precision_pct.toFixed(1)}%
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontFamily: 'monospace', color: '#cbd5e1' }}>
                        [{row.ci_low.toFixed(1)}%, {row.ci_high.toFixed(1)}%]
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontFamily: 'monospace', color: '#cbd5e1' }}>
                        {row.false_alarms_per_10k.toFixed(1)}
                      </td>
                      <td style={{ padding: '12px', color: '#cbd5e1', fontSize: '0.75rem' }}>
                        {row.guidance}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>

            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#94a3b8', fontStyle: 'italic' }}>
              Precision formula: P(Spoof | Alert) = (p * TPR) / [p * TPR + (1 - p) * FPR], using pooled leg-level TPR = 26.98% and clean FPR = 1.17%.
            </div>
          </div>
        </>
      )}
    </div>
  )
}
