import '@testing-library/jest-dom/vitest'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import OverviewPage from '../pages/OverviewPage'
import FlightDetailPage from '../pages/FlightDetailPage'
import SARPage from '../pages/SARPage'
import LimitationsPage from '../pages/LimitationsPage'

const FORBIDDEN_WORDS_REGEX = /\b(ok|safe|clear|assured)\b/i

describe('Phase 6 Strict Regulatory & Integrity Testing', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  // -------------------------------------------------------------------------
  // 1. Overview Page & Number Parity Rule
  // -------------------------------------------------------------------------
  it('Overview: numbers rendered in DOM exactly match the API response', async () => {
    const mockOverviewApiData = {
      tag: 'v0.3.2-verified',
      active_dataset: 'benchmark',
      dataset_fingerprint: {
        tag: 'v0.3.2-verified',
        name: 'Frozen Benchmark Dataset',
        seed: '3001-3003 (Pooled Clean)',
        flights: 18000,
        n_clean: 13410,
        n_spoof: 2729,
        n_jam: 1861,
        config_hash: 'b6011043368eca73',
        primary_unit: 'scheduled leg',
      },
      primary_unit: 'scheduled leg',
      tier_distribution: {
        no_alert: {
          count: 14654,
          share_pct: 81.41,
          description: 'Nominal trajectory; consistent barometric altimetry',
        },
        flagged_altitude_inconsistency: {
          count: 1485,
          share_pct: 8.25,
          description: 'Check (a) altitude discrepancy exceeded',
        },
        jamming_degraded: {
          count: 1861,
          share_pct: 10.34,
          description: 'Degraded GPS interference environment',
        },
        insufficient: {
          count: 0,
          share_pct: 0.0,
          description: 'Insufficient telemetry; system abstains',
        },
      },
      secondary_unit: {
        unit: 'continuous flight track (merged segment)',
        count: 5225,
        note: 'Consecutive timetable legs stitched into continuous multi-leg airframe tracks',
      },
      headline_box: {
        title: 'What this can and cannot do',
        bullets: [
          'Altitude-consistency detector only: evaluates barometric vs geometric altimetry discrepancy (Check a).',
          'Horizontal spoofing 0% recall: lateral track manipulation is not detected by altitude consistency.',
          'Multi-aircraft consensus inactive: Check (d) is disabled in v0.3 and does not contribute to detection.',
          'All results synthetic: benchmark evaluated on simulated ADS-B perturbations, not real-world air traffic.',
        ],
      },
      links: [],
    }

    vi.spyOn(globalThis, 'fetch').mockImplementation((url: RequestInfo | URL) => {
      if (url.toString().includes('/api/overview')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockOverviewApiData),
        } as Response)
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`))
    })

    const onNavMock = vi.fn()
    const { container } = render(<OverviewPage activeDataset="benchmark" onNavigate={onNavMock} />)

    await waitFor(() => {
      expect(screen.getByTestId('headline-limits-box')).toBeInTheDocument()
    })

    // Strict number checks against API:
    const noAlertElem = screen.getByTestId('tier-count-no_alert')
    expect(noAlertElem.textContent?.replace(/,/g, '')).toBe(
      mockOverviewApiData.tier_distribution.no_alert.count.toString()
    )

    const flaggedElem = screen.getByTestId('tier-count-flagged_altitude_inconsistency')
    expect(flaggedElem.textContent?.replace(/,/g, '')).toBe(
      mockOverviewApiData.tier_distribution.flagged_altitude_inconsistency.count.toString()
    )

    const jamElem = screen.getByTestId('tier-count-jamming_degraded')
    expect(jamElem.textContent?.replace(/,/g, '')).toBe(
      mockOverviewApiData.tier_distribution.jamming_degraded.count.toString()
    )

    const insufficientElem = screen.getByTestId('tier-count-insufficient')
    expect(insufficientElem.textContent?.replace(/,/g, '')).toBe(
      mockOverviewApiData.tier_distribution.insufficient.count.toString()
    )

    // Forbidden words test: must NOT contain "ok", "safe", "clear", "assured"
    const renderedText = container.textContent || ''
    const forbiddenMatches = renderedText.match(FORBIDDEN_WORDS_REGEX)
    expect(forbiddenMatches).toBeNull()
  })

  // -------------------------------------------------------------------------
  // 2. Flight Detail Page Rules (Zero Axis A Probability, uncalibrated_score only)
  // -------------------------------------------------------------------------
  it('Flight Detail: never renders Axis A probability; displays uncalibrated_score and supporting checks', async () => {
    const mockFlightDetail = {
      flight_id: 'x1007f8_1793875401',
      icao24: 'x1007f8',
      tier: 'flagged_altitude_inconsistency',
      tier_reasons: ['geo_baro_alt_anomaly'],
      check_a: {
        name: 'geo_baro_alt',
        label: 'Geometric vs Barometric Altitude Consistency',
        role: 'primary',
        flag: true,
        reasons: ['geo_baro_residual_exceeded: 351.1m > 120.0m'],
        residual: 351.1,
      },
      check_b: {
        name: 'kinematic_feasibility',
        label: 'Kinematic Feasibility (Speed / Climb Constraints)',
        role: 'supporting only',
        flag: false,
        reasons: [],
        residual: 0.74,
      },
      check_c: {
        name: 'pos_vel_consistency',
        label: 'Position-Velocity Vector Consistency',
        role: 'supporting only',
        flag: false,
        reasons: [],
        residual: 179.1,
      },
      check_d: {
        name: 'multi_aircraft_consensus',
        label: 'Multi-Aircraft Consensus',
        role: 'inactive',
        flag: false,
        reasons: [],
        residual: null,
        note: 'Implemented, inactive in v0.3, needs re-validation. Does not contribute to detection in v0.3.',
      },
      radiation: {
        tier: 'moderate',
        label: 'illustrative placeholder',
        relative_index: 2.975,
        notice: 'Illustrative placeholder pending resolution of radiation constants',
      },
      uncalibrated_score: 0.9922,
      flagged_window: { start_ts: 1793875731, end_ts: 1793882091 },
      points: [
        { ts: 1793875401, baro_alt_m: 10000, geo_alt_m: 10010, residual_m: 10, is_flagged: false },
        { ts: 1793875731, baro_alt_m: 10000, geo_alt_m: 10351, residual_m: 351, is_flagged: true },
      ],
    }

    vi.spyOn(globalThis, 'fetch').mockImplementation((url: RequestInfo | URL) => {
      const urlStr = url.toString()
      if (urlStr.includes('/api/flights')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              { flight_id: 'x1007f8_1793875401', icao24: 'x1007f8', tier: 'flagged_altitude_inconsistency' },
            ]),
        } as Response)
      }
      if (urlStr.includes('/api/flight-detail/')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockFlightDetail),
        } as Response)
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`))
    })

    const { container } = render(<FlightDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId('flight-tier-badge')).toBeInTheDocument()
    })

    // Rule: Uncalibrated score field must appear with its exact label
    const uncalibratedScoreContainer = screen.getByTestId('uncalibrated-score-container')
    expect(uncalibratedScoreContainer).toBeInTheDocument()
    expect(screen.getByTestId('uncalibrated_score')).toHaveTextContent('0.9922')
    expect(uncalibratedScoreContainer).toHaveTextContent('uncalibrated_score')

    // Rule: Checks roles
    expect(screen.getByTestId('check-b-card')).toHaveTextContent('SUPPORTING ONLY')
    expect(screen.getByTestId('check-c-card')).toHaveTextContent('SUPPORTING ONLY')
    expect(screen.getByTestId('check-d-card')).toHaveTextContent('INACTIVE')

    // Rule: Radiation labelled illustrative placeholder
    const radContainer = screen.getByTestId('radiation-exposure-container')
    expect(radContainer).toHaveTextContent('illustrative placeholder')

    // Rule: Zero probability for Axis A
    const allText = container.textContent || ''
    expect(allText).not.toMatch(/Axis A.*probability/i)
    expect(allText).not.toMatch(/calibrated_prob/i)
    expect(allText).not.toMatch(/probability:\s*\d+/i)

    // Rule: Forbidden words
    const forbiddenMatches = allText.match(FORBIDDEN_WORDS_REGEX)
    expect(forbiddenMatches).toBeNull()
  })

  // -------------------------------------------------------------------------
  // 3. SAR Page & Privacy Suppression Rule
  // -------------------------------------------------------------------------
  it('SAR: suppressed cells render "suppressed" and never expose counts; regions labelled "midpoint region"', async () => {
    const mockSarRows = [
      {
        family: 'A320-family',
        region: 'Eastern Mediterranean',
        month: '2026-11',
        n_flights_flagged: 79,
        n_silent: 34,
        sar: 0.4304,
        ci_low: 0.3269,
        ci_high: 0.5403,
        suppressed: false,
      },
      {
        family: 'A320-family',
        region: 'Western Europe',
        month: '2026-11',
        n_flights_flagged: null,
        n_silent: null,
        sar: null,
        ci_low: null,
        ci_high: null,
        suppressed: true,
      },
      {
        family: 'A350',
        region: 'North Atlantic',
        month: '2026-11',
        n_flights_flagged: null,
        n_silent: null,
        sar: null,
        ci_low: null,
        ci_high: null,
        suppressed: true,
      },
    ]

    vi.spyOn(globalThis, 'fetch').mockImplementation((url: RequestInfo | URL) => {
      if (url.toString().includes('/api/sar')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockSarRows),
        } as Response)
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`))
    })

    const { container } = render(<SARPage />)

    await waitFor(() => {
      expect(screen.getByTestId('sar-table')).toBeInTheDocument()
    })

    // Rule: One-line explanation must exist
    expect(screen.getByTestId('sar-definition-line')).toHaveTextContent(
      'SAR_hat is the silent share among flagged legs.'
    )

    // Rule: Column header labelled "Midpoint Region"
    expect(screen.getByText('Midpoint Region')).toBeInTheDocument()

    // Rule: No row or header called "control sector"
    const textContent = container.textContent || ''
    expect(textContent.toLowerCase()).not.toContain('control sector')

    // Rule: Suppressed cells MUST render "suppressed" and never expose counts
    const suppRow1Sample = screen.getByTestId('cell-sample-size-1')
    expect(suppRow1Sample).toHaveTextContent('suppressed')
    expect(suppRow1Sample.textContent).not.toMatch(/\d+/)

    const suppRow1Silent = screen.getByTestId('cell-silent-count-1')
    expect(suppRow1Silent).toHaveTextContent('suppressed')
    expect(suppRow1Silent.textContent).not.toMatch(/\d+/)

    const suppRow1Sar = screen.getByTestId('cell-sar-1')
    expect(suppRow1Sar).toHaveTextContent('suppressed')
    expect(suppRow1Sar.textContent).not.toMatch(/\d+/)

    // Rule: Published cell shows real count
    const pubSample = screen.getByTestId('cell-sample-size-0')
    expect(pubSample).toHaveTextContent('79')

    // Rule: Forbidden words
    const forbiddenMatches = textContent.match(FORBIDDEN_WORDS_REGEX)
    expect(forbiddenMatches).toBeNull()
  })

  // -------------------------------------------------------------------------
  // 4. Limitations Page & Base Rate Table
  // -------------------------------------------------------------------------
  it('Limitations: renders headline bullets and base-rate sensitivity table with no forbidden words', async () => {
    const mockLimitations = {
      tag: 'v0.3.2-verified',
      dataset_fingerprint: {
        tag: 'v0.3.2-verified',
        name: 'Frozen Benchmark Dataset',
        seed: '3001-3003 (Pooled Clean)',
        flights: 18000,
        primary_unit: 'scheduled leg',
        config_hash: 'b6011043368eca73',
      },
      bullets: [
        'Altitude-consistency detector only: evaluates barometric vs geometric altimetry discrepancy (Check a).',
        'Horizontal spoofing 0% recall: lateral track manipulation is not detected by altitude consistency.',
        'Multi-aircraft consensus inactive: Check (d) is disabled in v0.3 and does not contribute to detection.',
        'All results synthetic: benchmark evaluated on simulated ADS-B perturbations, not real-world air traffic.',
        'Abstention exercised only in the labelled rule-trigger demo and never in the benchmark.',
        'False alarms driven by the generator assumed barometric-fault rate (2% per point, 60 to 180 m).',
        'Radiation tables are illustrative placeholders.',
        'Threat base-rate impact: detector precision drops sharply in peacetime low-prevalence airspaces.',
      ],
      base_rate_table: [
        {
          scenario: '0.01% (Normal Peacetime)',
          prevalence_pct: 0.01,
          precision_pct: 0.2,
          ci_low: 0.2,
          ci_high: 0.3,
          false_alarms_per_10k: 116.9,
          guidance: 'Corroboration required',
        },
        {
          scenario: '17.47% (Benchmark Test Base Rate)',
          prevalence_pct: 17.47,
          precision_pct: 83.0,
          ci_low: 79.7,
          ci_high: 85.8,
          false_alarms_per_10k: 96.5,
          guidance: 'Tactical alerting warranted',
        },
      ],
    }

    vi.spyOn(globalThis, 'fetch').mockImplementation((url: RequestInfo | URL) => {
      if (url.toString().includes('/api/limitations')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockLimitations),
        } as Response)
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`))
    })

    const { container } = render(<LimitationsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('base-rate-table')).toBeInTheDocument()
    })

    expect(screen.getByText('0.01% (Normal Peacetime)')).toBeInTheDocument()
    expect(screen.getByText('0.2%')).toBeInTheDocument()
    expect(screen.getByText('83.0%')).toBeInTheDocument()

    // Forbidden words
    const allText = container.textContent || ''
    const forbiddenMatches = allText.match(FORBIDDEN_WORDS_REGEX)
    expect(forbiddenMatches).toBeNull()
  })

  // -------------------------------------------------------------------------
  // 5. Phase 8.1 Demo Fallback Disclosure Test
  // -------------------------------------------------------------------------
  it('FlightDetail: shows visible fallback banner and updates header flight ID on static demo substitution', async () => {
    const mockFallbackFlight = {
      flight_id: 'x603da7_1794073786',
      icao24: 'x603da7',
      tier: 'flagged_altitude_inconsistency',
      tier_reasons: ['geo_baro_discrepancy_exceeded'],
      check_a: {
        name: 'geo_baro_alt',
        label: 'Geometric vs Barometric Altitude Consistency',
        role: 'primary',
        flag: true,
        reasons: ['residual_exceeded_120m'],
        residual: 185.4,
      },
      check_b: { name: 'pos_vel_consistency', label: 'Position/Velocity Feasibility', role: 'supporting', flag: false, reasons: [] },
      check_c: { name: 'rf_integrity_degradation', label: 'ADS-B Integrity Degradation', role: 'supporting', flag: false, reasons: [] },
      check_d: { name: 'multi_aircraft_consensus', label: 'Multi-Aircraft Consensus (Inactive)', role: 'inactive', flag: false, reasons: [] },
      radiation: { tier: 'quiet', label: 'Quiet Solar Activity', relative_index: 1.0, notice: 'Illustrative context' },
      uncalibrated_score: 0.88,
      points: [
        { ts: 1794073786, baro_alt_m: 10000, geo_alt_m: 10200, residual_m: 200, is_flagged: true },
      ],
      _demo_fallback: true,
      _requested_flight_id: 'unknown_flight_9999',
    }

    vi.spyOn(globalThis, 'fetch').mockImplementation((url: RequestInfo | URL) => {
      const urlStr = url.toString()
      if (urlStr.includes('/api/flights')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve([
            { flight_id: 'unknown_flight_9999', icao24: 'unknown', tier: 'flagged_altitude_inconsistency' },
          ]),
        } as Response)
      }
      if (urlStr.includes('/api/flight-detail/')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockFallbackFlight),
        } as Response)
      }
      return Promise.reject(new Error(`Unhandled URL: ${url}`))
    })

    render(<FlightDetailPage />)

    await waitFor(
      () => {
        expect(screen.queryByText(/Loading flight telemetry points/i)).not.toBeInTheDocument()
      },
      { timeout: 3000 },
    )

    await waitFor(
      () => {
        expect(screen.getByTestId('static-demo-fallback-banner')).toBeInTheDocument()
      },
      { timeout: 3000 },
    )

    // Check banner text content across child nodes
    const banner = screen.getByTestId('static-demo-fallback-banner')
    expect(banner).toHaveTextContent(/Not available in the static demo\. Showing example flight x603da7_1794073786 instead/i)

    // Check page header shows the substituted flight's ID
    const headerId = screen.getByTestId('header-flight-id')
    expect(headerId).toHaveTextContent('x603da7_1794073786')
  })
})

