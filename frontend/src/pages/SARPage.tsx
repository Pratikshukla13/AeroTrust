import { useEffect, useState } from 'react'
import { Lock, Info } from 'lucide-react'

interface SARAggregateRow {
  family: string
  region: string
  month: string
  n_flights_flagged?: number | null
  n_silent?: number | null
  sar?: number | null
  ci_low?: number | null
  ci_high?: number | null
  suppressed: boolean
}

export default function SARPage() {
  const [sarRows, setSarRows] = useState<SARAggregateRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/sar')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`)
        return res.json()
      })
      .then((data: SARAggregateRow[]) => {
        setSarRows(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(`Failed to retrieve SAR metrics: ${err.message}`)
        setLoading(false)
      })
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Panel */}
      <div className="glass-panel" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h1 style={{ margin: '0 0 8px', fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
              Silent Acceptance Rate (SAR) Observatory
            </h1>
            {/* Exactly required one-line explanation */}
            <p
              data-testid="sar-definition-line"
              style={{ margin: 0, fontSize: '0.875rem', color: '#38bdf8', fontWeight: 600 }}
            >
              SAR_hat is the silent share among flagged legs.
            </p>
          </div>

          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '6px',
              backgroundColor: 'rgba(52, 211, 153, 0.12)',
              border: '1px solid rgba(52, 211, 153, 0.35)',
              color: '#34d399',
              fontSize: '0.75rem',
              fontWeight: 700,
            }}
          >
            <Lock size={12} aria-hidden="true" />
            <span>Differential Privacy Guardrail Active</span>
          </div>
        </div>

        {/* Privacy Policy Disclosure */}
        <div
          style={{
            marginTop: '16px',
            padding: '12px 16px',
            borderRadius: '8px',
            backgroundColor: 'rgba(30, 41, 59, 0.6)',
            border: '1px solid #334155',
            display: 'flex',
            gap: '12px',
            alignItems: 'flex-start',
          }}
        >
          <Info size={16} style={{ color: '#38bdf8', flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
          <div style={{ fontSize: '0.8125rem', color: '#cbd5e1', lineHeight: 1.5 }}>
            <strong>Privacy Policy (README Section 4.4 &amp; Phase 4.2):</strong> All counts aggregated strictly by airframe family &times; midpoint region.
            Any cell with fewer than 30 flagged flights, along with complementary cells required to prevent algebraic subtraction recovery, displays <em>suppressed</em> with zero counts exposed.
            Regions are categorized strictly by trajectory midpoint coordinates.
          </div>
        </div>
      </div>

      {loading && (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <p style={{ margin: 0, color: '#38bdf8', fontSize: '0.9375rem' }}>Loading SAR aggregates from API...</p>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ padding: '24px', borderLeft: '4px solid #ef4444' }}>
          <p style={{ margin: 0, color: '#fca5a5', fontSize: '0.875rem' }}>{error}</p>
        </div>
      )}

      {!loading && sarRows.length > 0 && (
        <div className="glass-panel" style={{ padding: '24px 28px', overflowX: 'auto' }}>
          <h2 style={{ margin: '0 0 16px', fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>
            Privacy-Preserving SAR Regional Breakdown
          </h2>

          <table
            data-testid="sar-table"
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '0.8125rem',
              textAlign: 'left',
            }}
          >
            <thead>
              <tr style={{ borderBottom: '2px solid #334155', color: '#94a3b8' }}>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>Aircraft Family</th>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>Midpoint Region</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>Sample Size (N_flagged)</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>Silent Count (N_silent)</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>SAR_hat</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'center' }}>Wilson 95% CI</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'center' }}>Publication Status</th>
              </tr>
            </thead>
            <tbody>
              {sarRows.map((row, idx) => {
                const isSuppressed = row.suppressed

                return (
                  <tr
                    key={idx}
                    data-testid={`sar-row-${row.family}-${row.region}`}
                    style={{
                      borderBottom: '1px solid #1e293b',
                      backgroundColor: isSuppressed ? 'rgba(15, 23, 42, 0.4)' : 'rgba(30, 41, 59, 0.4)',
                    }}
                  >
                    {/* Aircraft Family */}
                    <td style={{ padding: '12px', fontWeight: 700, color: '#f8fafc' }}>
                      {row.family}
                    </td>

                    {/* Midpoint Region (Strictly labelled Midpoint Region) */}
                    <td style={{ padding: '12px', color: '#cbd5e1' }}>
                      {row.region}
                    </td>

                    {/* Sample Size (N_flagged): strictly "suppressed" if suppressed */}
                    <td
                      style={{
                        padding: '12px',
                        textAlign: 'right',
                        fontFamily: isSuppressed ? 'inherit' : 'monospace',
                        color: isSuppressed ? '#94a3b8' : '#f8fafc',
                        fontStyle: isSuppressed ? 'italic' : 'normal',
                      }}
                      data-testid={`cell-sample-size-${idx}`}
                    >
                      {isSuppressed ? 'suppressed' : (row.n_flights_flagged?.toLocaleString() ?? '—')}
                    </td>

                    {/* Silent Count: strictly "suppressed" if suppressed */}
                    <td
                      style={{
                        padding: '12px',
                        textAlign: 'right',
                        fontFamily: isSuppressed ? 'inherit' : 'monospace',
                        color: isSuppressed ? '#94a3b8' : '#cbd5e1',
                        fontStyle: isSuppressed ? 'italic' : 'normal',
                      }}
                      data-testid={`cell-silent-count-${idx}`}
                    >
                      {isSuppressed ? 'suppressed' : (row.n_silent?.toLocaleString() ?? '—')}
                    </td>

                    {/* SAR_hat: strictly "suppressed" if suppressed */}
                    <td
                      style={{
                        padding: '12px',
                        textAlign: 'right',
                        fontWeight: isSuppressed ? 400 : 700,
                        color: isSuppressed ? '#94a3b8' : '#38bdf8',
                        fontStyle: isSuppressed ? 'italic' : 'normal',
                      }}
                      data-testid={`cell-sar-${idx}`}
                    >
                      {isSuppressed ? 'suppressed' : `${((row.sar ?? 0) * 100).toFixed(1)}%`}
                    </td>

                    {/* Wilson CI: strictly "suppressed" if suppressed */}
                    <td
                      style={{
                        padding: '12px',
                        textAlign: 'center',
                        color: isSuppressed ? '#94a3b8' : '#cbd5e1',
                        fontFamily: isSuppressed ? 'inherit' : 'monospace',
                        fontStyle: isSuppressed ? 'italic' : 'normal',
                      }}
                      data-testid={`cell-ci-${idx}`}
                    >
                      {isSuppressed
                        ? 'suppressed'
                        : `[${((row.ci_low ?? 0) * 100).toFixed(1)}%, ${((row.ci_high ?? 0) * 100).toFixed(1)}%]`}
                    </td>

                    {/* Publication Status Badge */}
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      {isSuppressed ? (
                        <span
                          style={{
                            fontSize: '0.6875rem',
                            fontWeight: 600,
                            padding: '3px 8px',
                            borderRadius: '4px',
                            backgroundColor: 'rgba(100, 116, 139, 0.2)',
                            color: '#94a3b8',
                            border: '1px solid rgba(100, 116, 139, 0.4)',
                          }}
                        >
                          suppressed
                        </span>
                      ) : (
                        <span
                          style={{
                            fontSize: '0.6875rem',
                            fontWeight: 700,
                            padding: '3px 8px',
                            borderRadius: '4px',
                            backgroundColor: 'rgba(56, 189, 248, 0.15)',
                            color: '#38bdf8',
                            border: '1px solid rgba(56, 189, 248, 0.4)',
                          }}
                        >
                          Published
                        </span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
