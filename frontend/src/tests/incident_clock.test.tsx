import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import IncidentClockPage from '../pages/IncidentClockPage'

describe('Phase 7: Incident Clock & Scoping Calculator Tests', () => {
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
                directive_date: '2025-11-29',
                aircraft_affected_total: 6000,
                aircraft_in_service: null,
                aircraft_undelivered: null,
                deliveries_context: 'Fewer than 100 remaining on 1 Dec 2025.',
                days_event_to_statement: 29,
                source_url: 'https://ad.easa.europa.eu/ad/2025-XXXX-E',
                verification_status: 'needs verification',
              },
              {
                case_id: 'A320-PANEL-2025',
                title: 'A320 Fuselage Panels Production Discrepancy',
                event_date: null,
                public_statement_date: null,
                directive_date: '2025-12-17',
                aircraft_affected_total: 628,
                aircraft_in_service: 177,
                aircraft_undelivered: 451,
                deliveries_context: null,
                days_event_to_statement: null,
                source_url: 'https://ad.easa.europa.eu/ad/US-2025-XXXX',
                verification_status: 'needs verification',
              },
              {
                case_id: 'A330-TOOL-2026',
                title: 'A330 Stray Assembly Tool Inspection',
                event_date: null,
                public_statement_date: null,
                directive_date: null,
                aircraft_affected_total: null,
                aircraft_in_service: null,
                aircraft_undelivered: null,
                deliveries_context:
                  'Zero deliveries in June and July 2026; nine in March to May 2026. Number of aircraft inspected not disclosed. Policy to the regulator due mid-November 2026.',
                days_event_to_statement: null,
                source_url: 'https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026',
                verification_status: 'needs verification',
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

  it('renders required mandatory disclosure copy', async () => {
    render(<IncidentClockPage />)
    const copyBanner = await screen.findByTestId('calculator-mandated-copy')
    expect(copyBanner.textContent).toContain(
      'This calculator turns public information into a scenario. It does not describe Airbus internal data or decisions. Scenario outputs depend on the inputs you enter.'
    )
  })

  it('UI test: renders "needs verification" for EVERY case until status is sourced', async () => {
    render(<IncidentClockPage />)
    const badgeSolar = await screen.findByTestId('badge-verification-A320-SOLAR-2025')
    const badgePanel = await screen.findByTestId('badge-verification-A320-PANEL-2025')
    const badgeTool = await screen.findByTestId('badge-verification-A330-TOOL-2026')

    expect(badgeSolar.textContent).toBe('needs verification')
    expect(badgePanel.textContent).toBe('needs verification')
    expect(badgeTool.textContent).toBe('needs verification')
  })

  it('renders A320 solar radiation timeline view with 29-day computed gap', async () => {
    render(<IncidentClockPage />)
    expect(screen.getByText('30 Oct 2025')).toBeDefined()
    expect(screen.getByText('28 Nov 2025')).toBeDefined()
    expect(screen.getByText('29 Nov 2025')).toBeDefined()
    expect(screen.getByText('29 Days')).toBeDefined()
    expect(
      screen.getByText(/reflects public disclosure timing only and says nothing about internal engineering/i)
    ).toBeDefined()
  })

  it('test: no preset contains an unsourced number (unsourced remain empty & highlighted)', async () => {
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

  it('test: formula with hand-computed values matches exactly', async () => {
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

  it('test: blank inputs produce NO money figure', async () => {
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

  it('test: entered value produces expected financial calculation', async () => {
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
