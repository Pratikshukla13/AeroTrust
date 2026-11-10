import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import IncidentClockPage from '../pages/IncidentClockPage'

describe('Phase 7, 7.1 & 7.2: Incident Clock & Scoping Calculator Tests', () => {
  beforeEach(() => {
    // Mock fetch for /api/incident-cases (Phase 7.2 updated schema & data)
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/incident-cases')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
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
                    description: 'Flight controls data corruption event occurs at cruise altitude. Axis B is exposure context, not a cause.',
                    source_url: null,
                    source_type: 'regulator',
                    url_status: 'unchecked',
                  },
                  {
                    date: '2025-11-28',
                    label: 'Airbus Alert & EASA Emergency AD Issued',
                    description: 'Airbus alert and EASA emergency directive issued 28 Nov 2025.',
                    source_url: null,
                    source_type: 'regulator',
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
                deliveries_context: '2025 delivery target cut 820 to 790 on 3 Dec 2025. EASA proposed directive published 17 Dec 2025. Later final directive to be confirmed.',
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
                    fact_referenced: 'Proposed directive published 17 Dec 2025 (177 in service, 451 in production).',
                  },
                  {
                    url: null,
                    title: 'Airbus Statement on Fuselage Panels',
                    source_type: 'manufacturer',
                    url_status: 'unchecked',
                    fact_referenced: 'Airbus public statement 2 Dec 2025 confirming 628 aircraft in scope.',
                  },
                ],
                dated_events: [
                  {
                    date: '2025-12-02',
                    label: 'Airbus Public Statement',
                    description: 'Airbus discloses 628 aircraft in scope.',
                    source_url: null,
                    source_type: 'manufacturer',
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
                    customer_allocated_or_other: null,
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
                deliveries_context: 'Zero deliveries in June and July 2026; 3, 2, 4 in March, April, May; one on 11 Aug 2026. Number of aircraft inspected not disclosed. Policy to regulator due mid-November 2026.',
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
                ],
                fleet_breakdowns: [],
              },
            ]),
        })
      }
      return Promise.resolve({ ok: false, status: 404 })
    }))
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders required mandatory disclosure copy', () => {
    render(<IncidentClockPage />)
    const copyBanner = screen.getByTestId('calculator-mandated-copy')
    expect(copyBanner.textContent).toContain(
      'This calculator turns public information into a scenario. It does not describe Airbus internal data or decisions. Scenario outputs depend on the inputs you enter.'
    )
  })

  it('renders exact mandatory radiation copy with exposure context notice', () => {
    render(<IncidentClockPage />)
    const exactRequiredCopy =
      'Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts have questioned whether the radiation level on that date was unusual.'
    const matchingElements = screen.getAllByText(new RegExp(exactRequiredCopy, 'i'))
    expect(matchingElements.length).toBeGreaterThanOrEqual(1)

    const decouplingNotes = screen.getAllByText(/Axis B is exposure context, not a cause/i)
    expect(decouplingNotes.length).toBeGreaterThanOrEqual(1)
  })

  it('verifies no page element contains forbidden solar causal phrase', () => {
    const { container } = render(<IncidentClockPage />)
    const text = container.textContent?.toLowerCase() || ''
    const forbidden = 'solar ' + 'storm ' + 'caused'
    expect(text.includes(forbidden)).toBe(false)
  })

  it('UI test: renders "needs verification" for EVERY case until status is sourced', async () => {
    render(<IncidentClockPage />)
    const badgeSolar = await screen.findByTestId('badge-verification-A320-SOLAR-2025')
    const badgePanel = await screen.findByTestId('badge-verification-A320-PANEL-2025')
    const badgeTool = await screen.findByTestId('badge-verification-A330NEO-TOOL-2026')

    expect(badgeSolar.textContent).toBe('needs verification')
    expect(badgePanel.textContent).toBe('needs verification')
    expect(badgeTool.textContent).toBe('needs verification')
  })

  it('UI test: renders "primary source missing" in red for null URLs and shows "unchecked" badge', async () => {
    render(<IncidentClockPage />)
    await screen.findByTestId('badge-verification-A320-SOLAR-2025')

    // Every case with null primary URL shows primary source missing
    expect(screen.getByTestId('primary-source-missing-A320-SOLAR-2025')).toBeDefined()
    expect(screen.getByTestId('primary-source-missing-A320-PANEL-2025')).toBeDefined()
    expect(screen.getByTestId('primary-source-missing-A330NEO-TOOL-2026')).toBeDefined()

    // Assert "unchecked" badge is displayed next to sources/breakdowns
    const uncheckedBadges = screen.getAllByText('unchecked')
    expect(uncheckedBadges.length).toBeGreaterThanOrEqual(3)
  })

  it('renders A320 solar radiation timeline view with 29-day computed gap', () => {
    render(<IncidentClockPage />)
    expect(screen.getAllByText('30 Oct 2025').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('28 Nov 2025').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('1 Dec 2025').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('29 Days')).toBeDefined()
  })

  it('renders Reuters breakdown with corrected labels and no parts supplier or airline fleet', async () => {
    render(<IncidentClockPage />)
    await screen.findByText(/Reuters Sourced Breakdown/i)

    const expectedText = '168 in service, 245 on assembly lines (about 100 due for delivery in 2025), 215 in earlier production.'
    expect(screen.getByText(expectedText)).toBeDefined()

    // Ensure forbidden strings do NOT appear in document text
    const containerText = document.body.textContent?.toLowerCase() || ''
    expect(containerText.includes('parts supplier')).toBe(false)
    expect(containerText.includes('airline fleet')).toBe(false)
  })

  it('renders A330neo with NONE PUBLISHED / UNKNOWN directive badge, updated scope note, and no "24 vs 4"', async () => {
    render(<IncidentClockPage />)
    await screen.findByText(/A330neo Stray Assembly Tool Inspection/i)

    // Directive status badge
    expect(screen.getByText(/DIRECTIVE: NONE PUBLISHED \/ UNKNOWN/i)).toBeDefined()

    // Scope note
    expect(screen.getByText(/Reports conflict: one says no retroactive fix is required/i)).toBeDefined()

    // Confirm "24 vs 4" does not appear in body
    const containerText = document.body.textContent || ''
    expect(containerText.includes('24 vs 4')).toBe(false)
  })

  it('test: A320 solar preset leaves days_to_scope empty and displays separate public gap helper', () => {
    render(<IncidentClockPage />)

    // Click Solar Preset
    const btnSolar = screen.getByTestId('btn-preset-solar')
    fireEvent.click(btnSolar)

    const inputDays = screen.getByTestId('input-days-to-scope') as HTMLInputElement
    const inputInService = screen.getByTestId('input-in-service') as HTMLInputElement
    const inputUndelivered = screen.getByTestId('input-undelivered') as HTMLInputElement

    // Phase 7.2 rule: days_to_scope MUST remain strictly empty in the preset
    expect(inputDays.value).toBe('')
    expect(inputInService.value).toBe('')
    expect(inputUndelivered.value).toBe('')

    // Check display-only callout with helper text
    const callout = screen.getByTestId('public-statement-gap-callout')
    expect(callout.textContent).toContain('days_event_to_public_statement = 29 Days')
    expect(callout.textContent).toContain(
      "This is the public gap between the incident and Airbus's statement. It is not a hold period and not a scoping time."
    )
  })

  it('test: panels preset populates sourced fields only', () => {
    render(<IncidentClockPage />)

    const btnPanel = screen.getByTestId('btn-preset-panel')
    fireEvent.click(btnPanel)

    const inputDays = screen.getByTestId('input-days-to-scope') as HTMLInputElement
    const inputInService = screen.getByTestId('input-in-service') as HTMLInputElement
    const inputUndelivered = screen.getByTestId('input-undelivered') as HTMLInputElement

    expect(inputDays.value).toBe('')
    expect(inputInService.value).toBe('177')
    expect(inputUndelivered.value).toBe('451')
  })

  it('test: formula with hand-computed values matches exactly', () => {
    render(<IncidentClockPage />)

    const inputDays = screen.getByTestId('input-days-to-scope')
    const inputInService = screen.getByTestId('input-in-service')
    const inputUndelivered = screen.getByTestId('input-undelivered')
    const inputRate = screen.getByTestId('input-baseline-rate')
    const inputShare = screen.getByTestId('input-share-recovered')

    // Scenario:
    // days = 30
    // in-service = 100, undelivered = 50 -> held = 150
    // rate = 60/mo
    // share recovered = 25%
    fireEvent.change(inputDays, { target: { value: '30' } })
    fireEvent.change(inputInService, { target: { value: '100' } })
    fireEvent.change(inputUndelivered, { target: { value: '50' } })
    fireEvent.change(inputRate, { target: { value: '60' } })
    fireEvent.change(inputShare, { target: { value: '25' } })

    // a. aircraft_days_held = 150 * 30 = 4,500
    const valAircraftDaysHeld = screen.getByTestId('val-aircraft-days-held')
    expect(valAircraftDaysHeld.textContent).toContain('4,500')

    // b. Model A: gross = 60 * (30/30) = 60; net = 60 * (1 - 0.25) = 45.0
    const valModelANet = screen.getByTestId('val-model-a-net')
    expect(valModelANet.textContent).toContain('45.0')

    // c. Model B: undelivered * days = 50 * 30 = 1,500
    const valModelBDays = screen.getByTestId('val-model-b-days')
    expect(valModelBDays.textContent).toContain('1,500')

    // One day cost: 150 aircraft-days / day
    const valOneDayAircraftDays = screen.getByTestId('val-one-day-aircraft-days')
    expect(valOneDayAircraftDays.textContent).toContain('150')
  })

  it('test: blank inputs produce NO money figure', () => {
    render(<IncidentClockPage />)

    const inputDays = screen.getByTestId('input-days-to-scope')
    const inputInService = screen.getByTestId('input-in-service')
    const inputUndelivered = screen.getByTestId('input-undelivered')
    const inputRate = screen.getByTestId('input-baseline-rate')
    const inputValue = screen.getByTestId('input-value-per-aircraft') as HTMLInputElement

    fireEvent.change(inputDays, { target: { value: '30' } })
    fireEvent.change(inputInService, { target: { value: '100' } })
    fireEvent.change(inputUndelivered, { target: { value: '50' } })
    fireEvent.change(inputRate, { target: { value: '60' } })

    expect(inputValue.value).toBe('')

    // Financial impact card must show '--' and NOT contain '$'
    const valFinancial = screen.getByTestId('val-financial-impact')
    expect(valFinancial.textContent).toBe('--')

    const valOneDayMoney = screen.getByTestId('val-one-day-money')
    expect(valOneDayMoney.textContent).toContain('No money figure')
    expect(valOneDayMoney.textContent).not.toContain('$')

    const table = screen.getByTestId('sensitivity-table')
    expect(table.textContent).not.toContain('$')
  })

  it('test: entered value produces expected financial calculation', () => {
    render(<IncidentClockPage />)

    const inputDays = screen.getByTestId('input-days-to-scope')
    const inputInService = screen.getByTestId('input-in-service')
    const inputUndelivered = screen.getByTestId('input-undelivered')
    const inputRate = screen.getByTestId('input-baseline-rate')
    const inputShare = screen.getByTestId('input-share-recovered')
    const inputValue = screen.getByTestId('input-value-per-aircraft')

    // 30 days, 30/mo, 0% recovery, $100M/aircraft -> 30 aircraft lost = $3.00 B
    fireEvent.change(inputDays, { target: { value: '30' } })
    fireEvent.change(inputInService, { target: { value: '0' } })
    fireEvent.change(inputUndelivered, { target: { value: '10' } })
    fireEvent.change(inputRate, { target: { value: '30' } })
    fireEvent.change(inputShare, { target: { value: '0' } })
    fireEvent.change(inputValue, { target: { value: '100000000' } })

    const valFinancial = screen.getByTestId('val-financial-impact')
    expect(valFinancial.textContent).toContain('$3.00 B')
  })
})
