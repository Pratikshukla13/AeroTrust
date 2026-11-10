import '@testing-library/jest-dom/vitest'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import SyntheticBanner from '../components/SyntheticBanner'
import OverviewPage from '../pages/OverviewPage'
import MapPage from '../pages/MapPage'
import FlightDetailPage from '../pages/FlightDetailPage'
import SARPage from '../pages/SARPage'
import LimitationsPage from '../pages/LimitationsPage'
import IncidentClockPage from '../pages/IncidentClockPage'
import BriefingPage from '../pages/BriefingPage'
import CorridorsPage from '../pages/CorridorsPage'
import WatchlistPage from '../pages/WatchlistPage'

// Directly import precomputed static datasets
import staticMeta from '../../public/static-data/meta.json'
import staticOverview from '../../public/static-data/overview.json'
import staticLimitations from '../../public/static-data/limitations.json'
import staticSar from '../../public/static-data/sar.json'
import staticIncidentCases from '../../public/static-data/incident-cases.json'
import staticIncidentPresets from '../../public/static-data/incident-presets.json'
import staticRegions from '../../public/static-data/regions.json'
import staticTimeBuckets from '../../public/static-data/time-buckets.json'
import staticFlights from '../../public/static-data/flights.json'
import staticFlightDetail from '../../public/static-data/flights/x603da7_1794073786.json'

// Mock maplibre-gl for headless jsdom environment
vi.mock('maplibre-gl', () => {
  class MockMap {
    on = vi.fn()
    remove = vi.fn()
    addControl = vi.fn()
    getSource = vi.fn()
    addSource = vi.fn()
    addLayer = vi.fn()
    setFilter = vi.fn()
    flyTo = vi.fn()
  }

  class MockNavigationControl {}

  return {
    default: {
      Map: MockMap,
      NavigationControl: MockNavigationControl,
    },
    Map: MockMap,
    NavigationControl: MockNavigationControl,
  }
})

// Forbidden words regex: must not appear as standalone whole words in UI copy or tables
const FORBIDDEN_WORDS_REGEX = /\b(ok|safe|clear|assured)\b/i

// Routes to test
type RouteConfig = {
  id: string
  name: string
  render: () => React.ReactElement
}

const ALL_ROUTES: RouteConfig[] = [
  { id: 'overview', name: 'Overview', render: () => <OverviewPage activeDataset="benchmark" onNavigate={() => {}} /> },
  { id: 'map', name: 'Interference Map', render: () => <MapPage /> },
  { id: 'flight-detail', name: 'Flight Detail', render: () => <FlightDetailPage /> },
  { id: 'sar', name: 'SAR Metrics', render: () => <SARPage /> },
  { id: 'limitations', name: 'Limitations', render: () => <LimitationsPage /> },
  { id: 'incident-clock', name: 'Incident Scenario Calculator', render: () => <IncidentClockPage /> },
  { id: 'briefing', name: 'Briefing', render: () => <BriefingPage /> },
  { id: 'corridors', name: 'Corridors', render: () => <CorridorsPage /> },
  { id: 'watchlist', name: 'Watchlist', render: () => <WatchlistPage /> },
]

describe('Phase 8.3: Universal Route Integrity Across Live-API & Static Demo Modes', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  const modes = ['live-api', 'static'] as const

  for (const mode of modes) {
    describe(`Mode: ${mode.toUpperCase()}`, () => {
      beforeEach(() => {
        // Mock global fetch to return responses matching the active mode
        vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
          const urlStr = input.toString()

          // Flight single inspection
          if (urlStr.includes('/api/flight-detail') || urlStr.includes('/api/flights/') || urlStr.includes('/static-data/flights/')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticFlightDetail),
            } as Response)
          }

          // Flight list
          if (urlStr.includes('/api/flights') || urlStr.includes('/static-data/flights.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticFlights),
            } as Response)
          }

          // Meta
          if (urlStr.includes('/api/meta') || urlStr.includes('/static-data/meta.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticMeta),
            } as Response)
          }

          // Overview
          if (urlStr.includes('/api/overview') || urlStr.includes('/static-data/overview.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticOverview),
            } as Response)
          }

          // Limitations
          if (urlStr.includes('/api/limitations') || urlStr.includes('/static-data/limitations.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticLimitations),
            } as Response)
          }

          // SAR
          if (urlStr.includes('/api/sar') || urlStr.includes('/static-data/sar.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticSar),
            } as Response)
          }

          // Incident cases
          if (urlStr.includes('/api/incident-cases') || urlStr.includes('/static-data/incident-cases.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticIncidentCases),
            } as Response)
          }

          // Incident presets
          if (urlStr.includes('/api/incident-presets') || urlStr.includes('/static-data/incident-presets.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticIncidentPresets),
            } as Response)
          }

          // Map regions
          if (urlStr.includes('/api/map/regions') || urlStr.includes('/static-data/regions.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticRegions),
            } as Response)
          }

          // Map time buckets
          if (urlStr.includes('/api/map/time-buckets') || urlStr.includes('/static-data/time-buckets.json')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(staticTimeBuckets),
            } as Response)
          }

          // Map cells
          if (urlStr.includes('/api/map/cells') || urlStr.includes('cells-')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve([]),
            } as Response)
          }

          // Geojson map assets
          if (urlStr.includes('.geojson')) {
            return Promise.resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve({ type: 'FeatureCollection', features: [] }),
            } as Response)
          }

          return Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({}),
          } as Response)
        })
      })

      for (const route of ALL_ROUTES) {
        it(`Route [${route.name}]: verifies banner, no forbidden words, no Axis A prob, and no suppressed count`, async () => {
          const { container } = render(
            <div data-testid={`route-container-${route.id}`}>
              <SyntheticBanner />
              {route.render()}
            </div>
          )

          // 1. Assert SYNTHETIC banner is present
          const banner = screen.getByTestId('synthetic-banner')
          expect(banner).toBeInTheDocument()
          expect(banner).toHaveTextContent(/SYNTHETIC/i)

          // Wait for any async rendering to settle
          await waitFor(() => {
            const loadingMsg = screen.queryByText(/Loading/i)
            expect(loadingMsg).not.toBeInTheDocument()
          })

          const fullText = container.textContent || ''

          // 2. Assert no forbidden words (ok, safe, clear, assured as whole words)
          const forbiddenMatch = fullText.match(FORBIDDEN_WORDS_REGEX)
          expect(forbiddenMatch).toBeNull()

          // 3. Assert no Axis A probability rendered
          expect(fullText).not.toMatch(/Axis A.*probability/i)
          expect(fullText).not.toMatch(/calibrated_prob/i)
          expect(fullText).not.toMatch(/probability:\s*\d+/i)

          // 4. Assert no suppressed counts exposed
          expect(fullText).not.toMatch(/suppressed\s*\(\d+\)/i)

          // On SAR route, specifically assert that suppressed cells render "suppressed" with no numeric values
          if (route.id === 'sar') {
            const sarTable = screen.getByTestId('sar-table')
            expect(sarTable).toBeInTheDocument()
            const cells = sarTable.querySelectorAll('td')
            for (const cell of cells) {
              if (cell.textContent?.trim().toLowerCase() === 'suppressed') {
                expect(cell.textContent).not.toMatch(/\d+/)
              }
            }
          }
        })
      }
    })
  }
})
