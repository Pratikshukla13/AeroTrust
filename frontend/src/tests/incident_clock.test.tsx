import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import IncidentClockPage from '../pages/IncidentClockPage'

describe('Phase 7 & 7.1: Incident Clock & Scoping Calculator Tests', () => {
  beforeEach(() => {
    // Mock fetch for /api/incident-cases
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
                    description: 'Flight controls data corruption event occurs at cruise altitude.',
                    source_url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
                    source_type: 'regulator',
                  },
                  {
                    date: '2025-11-28',
                    label: 'Airbus Alert & EASA Emergency AD Issued',
                    description: 'Airbus alert and EASA emergency directive issued 28 Nov 2025.',
                    source_url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
                    source_type: 'regulator',
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
                source_url: 'https://ad.easa.europa.eu/ad/US-2025-XXXX-Proposed',
                source_type: 'regulator',
                verification_status: 'needs verification',
                sources: [
                  {
                    url: 'https://ad.easa.europa.eu/ad/US-2025-XXXX-Proposed',
                    title: 'EASA Proposed Airworthiness Directive (PAD)',
                    source_type: 'regulator',
                    fact_referenced: 'Proposed directive published 17 Dec 2025 (177 in service, 451 in production).',
                  },
                  {
                    url: 'https://www.airbus.com/en/newsroom/press-releases/2025-12-a320-fuselage-statement',
                    title: 'Airbus Public Statement on Fuselage Panels',
                    source_type: 'manufacturer',
                    fact_referenced: 'Airbus public statement 2 Dec 2025 confirming 628 aircraft in scope.',
                  },
                ],
                dated_events: [
                  {
                    date: '2025-12-02',
                    label: 'Airbus Public Statement',
                    description: 'Airbus discloses 628 aircraft in scope.',
                    source_url: 'https://www.airbus.com/en/newsroom/press-releases/2025-12-a320-fuselage-statement',
                    source_type: 'manufacturer',
                  },
                ],
                fleet_breakdowns: [
                  {
                    name: 'EASA Proposed Airworthiness Directive',
                    source_type: 'regulator',
                    in_service: 177,
                    undelivered_or_production: 451,
                    customer_allocated_or_other: null,
                    total: 628,
                    notes: 'Published 17 Dec 2025: 177 in-service, 451 in production.',
                  },
                  {
                    name: 'Reuters Industry Investigation',
                    source_type: 'wire',
                    in_service: 168,
                    undelivered_or_production: 245,
                    customer_allocated_or_other: 215,
                    total: 628,
                    notes: 'Secondary sourced breakdown: 168 airline fleet, 245 assembly plant, 215 parts supplier.',
                  },
                ],
              },
              {
                case_id: 'A330NEO-TOOL-2026',
                title: 'A330neo Stray Assembly Tool Inspection',
                event_date: null,
                public_statement_date: null,
                directive_date: null,
                directive_status: 'proposed',
                aircraft_affected_total: null,
                aircraft_in_service: null,
                aircraft_undelivered: null,
                deliveries_context: 'Zero deliveries in June and July 2026; 3, 2, 4 in March, April, May; one on 11 Aug 2026. Number of aircraft inspected not disclosed. Policy to regulator due mid-November 2026.',
                in_service_scope_notes: 'conflicting reports, needs verification',
                days_event_to_statement: null,
                source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
                source_type: 'manufacturer',
                verification_status: 'needs verification',
                sources: [
                  {
                    url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
                    title: 'Airbus Commercial Aircraft Monthly Deliveries File',
                    source_type: 'manufacturer',
                    fact_referenced: 'Deliveries log: 0 in June/July 2026, 3 in March, 2 in April, 4 in May, 1 on 11 Aug 2026.',
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

  it('renders exact mandatory radiation copy and decoupling note', () => {
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

  it('renders A320 solar radiation timeline view with 29-day computed gap', () => {
    render(<IncidentClockPage />)
    expect(screen.getAllByText('30 Oct 2025').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('28 Nov 2025').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('1 Dec 2025').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('29 Days')).toBeDefined()
    expect(screen.getAllByText(/Axis B is exposure context, not a cause/i).length).toBeGreaterThanOrEqual(1)
  })

  it('renders dual breakdowns for A320 panels and conflicting reports for A330neo', async () => {
    render(<IncidentClockPage />)
    // Wait for async fetch to set state
    await screen.findByText(/EASA Proposed Airworthiness Directive/i)

    // A320 panels dual breakdown
    expect(screen.getByText(/Reuters Industry Investigation/i)).toBeDefined()
    expect(screen.getByText(/168 in service/i)).toBeDefined()
    expect(screen.getByText(/245 production\/undelivered/i)).toBeDefined()
    expect(screen.getByText(/215 customer-allocated/i)).toBeDefined()

    // A330neo conflicting reports notice
    expect(screen.getByText(/conflicting reports, needs verification/i)).toBeDefined()
    expect(screen.getByText(/A330neo Stray Assembly Tool Inspection/i)).toBeDefined()
  })

  it('renders primary source links and source_type badges', async () => {
    render(<IncidentClockPage />)
    await screen.findByText(/EASA Emergency Airworthiness Directive/i)
    const badges = screen.getAllByText(/regulator|manufacturer|wire/i)
    expect(badges.length).toBeGreaterThan(0)
    expect(screen.getByText('EASA Emergency Airworthiness Directive')).toBeDefined()
    expect(screen.getByText('Airbus Alert Notification to Operators')).toBeDefined()
  })

  it('test: no preset contains an unsourced number (unsourced remain empty & highlighted)', () => {
    render(<IncidentClockPage />)

    // Click Solar Preset
    const btnSolar = screen.getByTestId('btn-preset-solar')
    fireEvent.click(btnSolar)

    const inputDays = screen.getByTestId('input-days-to-scope') as HTMLInputElement
    const inputInService = screen.getByTestId('input-in-service') as HTMLInputElement
    const inputUndelivered = screen.getByTestId('input-undelivered') as HTMLInputElement
    const inputRate = screen.getByTestId('input-baseline-rate') as HTMLInputElement
    const inputShare = screen.getByTestId('input-share-recovered') as HTMLInputElement
    const inputValue = screen.getByTestId('input-value-per-aircraft') as HTMLInputElement

    // Only days_to_scope (29) is sourced; held aircraft are unsourced and must be empty
    expect(inputDays.value).toBe('29')
    expect(inputInService.value).toBe('')
    expect(inputUndelivered.value).toBe('')
    expect(inputRate.value).toBe('')
    expect(inputShare.value).toBe('')
    expect(inputValue.value).toBe('')

    // Click Panels Preset
    const btnPanel = screen.getByTestId('btn-preset-panel')
    fireEvent.click(btnPanel)

    // In-service (177) and Undelivered (451) are sourced; days_to_scope is unsourced and must be empty
    expect(inputDays.value).toBe('')
    expect(inputInService.value).toBe('177')
    expect(inputUndelivered.value).toBe('451')
    expect(inputRate.value).toBe('')
    expect(inputShare.value).toBe('')
    expect(inputValue.value).toBe('')

    // Click Stray Tool Preset
    const btnTool = screen.getByTestId('btn-preset-tool')
    fireEvent.click(btnTool)

    // All calculator numerical inputs are unsourced -> all empty
    expect(inputDays.value).toBe('')
    expect(inputInService.value).toBe('')
    expect(inputUndelivered.value).toBe('')
    expect(inputRate.value).toBe('')
    expect(inputShare.value).toBe('')
    expect(inputValue.value).toBe('')
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

    // Value input is strictly BLANK
    expect(inputValue.value).toBe('')

    // Financial impact card must show '--' and NOT contain '$'
    const valFinancial = screen.getByTestId('val-financial-impact')
    expect(valFinancial.textContent).toBe('--')

    // One-day money callout must state no money figure
    const valOneDayMoney = screen.getByTestId('val-one-day-money')
    expect(valOneDayMoney.textContent).toContain('No money figure')
    expect(valOneDayMoney.textContent).not.toContain('$')

    // Sensitivity table financial column must show '--'
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
