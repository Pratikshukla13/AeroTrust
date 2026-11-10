/**
 * Static Demo & Offline Interceptor for AeroTrust Frontend.
 *
 * When VITE_STATIC_DEMO is true (or when offline / backend unreachable),
 * routes API calls to precomputed static JSON snapshots dumped from frozen tag v0.3.2-verified.
 */

const IS_STATIC_DEMO = import.meta.env.VITE_STATIC_DEMO === 'true' || import.meta.env.MODE === 'demo'

export function setupStaticInterceptor() {
  const originalFetch = window.fetch

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const urlString = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url

    // If request is not an API call, let browser fetch handle it
    if (!urlString.includes('/api/')) {
      return originalFetch(input, init)
    }

    // If static demo mode is explicitly enabled, route directly to static snapshots
    if (IS_STATIC_DEMO) {
      return handleStaticRoute(urlString, originalFetch)
    }

    // In live mode, attempt real fetch first; gracefully fall back to static snapshot if offline / connection refused
    try {
      const response = await originalFetch(input, init)
      if (response.ok || response.status === 304) {
        return response
      }
      // If endpoint returned 404 or 5xx, try static fallback
      return handleStaticRoute(urlString, originalFetch)
    } catch {
      // Network error (backend down / offline preview) -> seamless static fallback
      return handleStaticRoute(urlString, originalFetch)
    }
  }
}

async function handleStaticRoute(urlString: string, fallbackFetch: typeof window.fetch): Promise<Response> {
  const parsed = new URL(urlString, window.location.origin)
  const path = parsed.pathname
  const params = parsed.searchParams

  try {
    if (path.endsWith('/api/meta')) {
      return fallbackFetch('/static-data/meta.json')
    }

    if (path.endsWith('/api/overview')) {
      const dataset = params.get('dataset')
      if (dataset === 'rule_trigger_demo') {
        return fallbackFetch('/static-data/overview-demo.json')
      }
      return fallbackFetch('/static-data/overview.json')
    }

    if (path.endsWith('/api/limitations')) {
      return fallbackFetch('/static-data/limitations.json')
    }

    if (path.endsWith('/api/sar')) {
      return fallbackFetch('/static-data/sar.json')
    }

    if (path.endsWith('/api/incident-cases')) {
      return fallbackFetch('/static-data/incident-cases.json')
    }

    if (path.endsWith('/api/incident-presets')) {
      return fallbackFetch('/static-data/incident-presets.json')
    }

    if (path.endsWith('/api/map/regions')) {
      return fallbackFetch('/static-data/regions.json')
    }

    if (path.endsWith('/api/map/time-buckets')) {
      return fallbackFetch('/static-data/time-buckets.json')
    }

    if (path.endsWith('/api/map/cells')) {
      const region = params.get('region')
      const timeBucket = params.get('time_bucket')
      const resp = await fallbackFetch('/static-data/cells-all.json')
      if (resp.ok && (region || timeBucket)) {
        const allCells = await resp.json()
        const filtered = allCells.filter((c: any) => {
          if (region && region !== 'All Regions' && c.region !== region) return false
          if (timeBucket && c.time_bucket !== Number(timeBucket)) return false
          return true
        })
        return new Response(JSON.stringify(filtered), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      }
      return fallbackFetch('/static-data/cells-default.json')
    }

    if (path.endsWith('/api/flights')) {
      const tier = params.get('tier')
      const resp = await fallbackFetch('/static-data/flights.json')
      if (resp.ok && tier) {
        const flights = await resp.json()
        const filtered = flights.filter((f: any) => f.tier === tier)
        return new Response(JSON.stringify(filtered), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      }
      return resp
    }

    if (path.includes('/api/flight-detail/')) {
      const segments = path.split('/')
      const flightId = segments[segments.length - 1]
      const detailResp = await fallbackFetch(`/static-data/flights/${flightId}.json`)
      if (detailResp.ok) {
        return detailResp
      }
      // Fallback to first available dumped flight detail
      return fallbackFetch('/static-data/flights/x603da7_1794073786.json')
    }
  } catch (err) {
    console.warn('[StaticDemo] Interceptor fallback error:', err)
  }

  // Fallback to empty JSON
  return new Response(JSON.stringify({}), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  })
}
