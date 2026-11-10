import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapPin, X } from 'lucide-react'

interface MapCell {
  h3_cell: string
  time_bucket: number
  region: string
  status: string
  n_aircraft: number
  reasons: string[]
  lat: number
  lon: number
  boundary: number[][]
}

export default function MapPage() {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  // Filter States
  const [regions, setRegions] = useState<string[]>([])
  const [selectedRegion, setSelectedRegion] = useState<string>('All Regions')
  const [timeBuckets, setTimeBuckets] = useState<number[]>([])
  const [selectedTimeBucket, setSelectedTimeBucket] = useState<number | null>(null)

  // Cells Data & Clicked Cell State
  const [cells, setCells] = useState<MapCell[]>([])
  const [selectedCell, setSelectedCell] = useState<MapCell | null>(null)
  const [loadingCells, setLoadingCells] = useState(false)

  // 1. Fetch available filter options
  useEffect(() => {
    fetch('/api/map/regions')
      .then((res) => res.json())
      .then((data: string[]) => setRegions(data))
      .catch(() => setRegions(['All Regions', 'Eastern Mediterranean', 'Baltic', 'Black Sea', 'Middle East', 'Western Europe']))

    fetch('/api/map/time-buckets')
      .then((res) => res.json())
      .then((data: number[]) => {
        setTimeBuckets(data)
        if (data && data.length > 0) {
          setSelectedTimeBucket(data[0])
        }
      })
      .catch(() => {})
  }, [])

  // 2. Initialize Offline MapLibre GL instance
  useEffect(() => {
    if (!mapContainerRef.current) return

    const offlineStyle: maplibregl.StyleSpecification = {
      version: 8,
      name: 'AeroTrust Offline Vector',
      sources: {
        'natural-earth-land': {
          type: 'geojson',
          data: '/data/ne_110m_land.geojson',
        },
        'natural-earth-countries': {
          type: 'geojson',
          data: '/data/ne_110m_admin_0_countries.geojson',
        },
      },
      layers: [
        {
          id: 'ocean-background',
          type: 'background',
          paint: {
            'background-color': '#080d1a',
          },
        },
        {
          id: 'landmass',
          type: 'fill',
          source: 'natural-earth-land',
          paint: {
            'fill-color': '#131c2e',
            'fill-opacity': 0.95,
          },
        },
        {
          id: 'country-borders',
          type: 'line',
          source: 'natural-earth-countries',
          paint: {
            'line-color': '#2a3a55',
            'line-width': 1,
          },
        },
      ],
    }

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: offlineStyle,
      center: [28.0, 48.0],
      zoom: 3.5,
      maxZoom: 9,
      minZoom: 1.5,
      attributionControl: false,
    })

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right')

    map.on('load', () => {
      setMapLoaded(true)
    })

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  // 3. Fetch spatial H3 cells whenever filters change
  useEffect(() => {
    let url = '/api/map/cells?limit=400'
    if (selectedRegion && selectedRegion !== 'All Regions') {
      url += `&region=${encodeURIComponent(selectedRegion)}`
    }
    if (selectedTimeBucket !== null) {
      url += `&time_bucket=${selectedTimeBucket}`
    }

    setLoadingCells(true)
    fetch(url)
      .then((res) => res.json())
      .then((data: MapCell[]) => {
        setCells(data)
        setLoadingCells(false)
      })
      .catch(() => {
        setLoadingCells(false)
      })
  }, [selectedRegion, selectedTimeBucket])

  // 4. Update MapLibre GeoJSON layers with H3 cells
  useEffect(() => {
    const map = mapRef.current
    if (!map || !mapLoaded) return

    const sourceId = 'h3-interference-cells'
    const fillLayerId = 'h3-cells-fill'
    const lineLayerId = 'h3-cells-line'

    // Format cells as GeoJSON FeatureCollection
    const geojsonData: any = {
      type: 'FeatureCollection',
      features: cells.map((cell) => ({
        type: 'Feature',
        properties: {
          h3_cell: cell.h3_cell,
          status: cell.status,
          region: cell.region,
          n_aircraft: cell.n_aircraft,
          reasons: JSON.stringify(cell.reasons),
          time_bucket: cell.time_bucket,
        },
        geometry: {
          type: 'Polygon',
          coordinates: [cell.boundary],
        },
      })),
    }

    const existingSource = map.getSource(sourceId) as maplibregl.GeoJSONSource
    if (existingSource) {
      existingSource.setData(geojsonData)
    } else {
      map.addSource(sourceId, {
        type: 'geojson',
        data: geojsonData,
      })

      // Layer 1: Fill colored by status tier (jamming_degraded -> amber, insufficient -> purple)
      map.addLayer({
        id: fillLayerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': [
            'match',
            ['get', 'status'],
            'jamming_degraded',
            '#f59e0b',
            'insufficient',
            '#8b5cf6',
            '#38bdf8',
          ],
          'fill-opacity': 0.65,
        },
      })

      // Layer 2: Outline
      map.addLayer({
        id: lineLayerId,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': [
            'match',
            ['get', 'status'],
            'jamming_degraded',
            '#fbbf24',
            'insufficient',
            '#a855f7',
            '#0284c7',
          ],
          'line-width': 1.5,
        },
      })

      // Click handler for cell inspection
      map.on('click', fillLayerId, (e) => {
        if (!e.features || e.features.length === 0) return
        const feat = e.features[0]
        const props = feat.properties as any
        const reasonsParsed = typeof props.reasons === 'string' ? JSON.parse(props.reasons) : props.reasons

        setSelectedCell({
          h3_cell: props.h3_cell,
          status: props.status,
          region: props.region,
          n_aircraft: Number(props.n_aircraft),
          reasons: reasonsParsed || [],
          time_bucket: Number(props.time_bucket),
          lat: 0,
          lon: 0,
          boundary: [],
        })
      })

      map.on('mouseenter', fillLayerId, () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', fillLayerId, () => {
        map.getCanvas().style.cursor = ''
      })
    }
  }, [cells, mapLoaded])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Controls Bar: Filters for Region and Time Bucket */}
      <div className="glass-panel" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
              Interference Observatory Map
            </h1>
            <p style={{ margin: '3px 0 0', fontSize: '0.8125rem', color: '#94a3b8' }}>
              MapLibre GL instance powered by local Natural Earth vectors. H3 cells colored strictly by <code>jamming_degraded</code> or <code>insufficient</code>.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            {/* Region Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label htmlFor="region-filter" style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Region:
              </label>
              <select
                id="region-filter"
                data-testid="region-filter-select"
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                style={{
                  padding: '6px 10px',
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid #475569',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                }}
              >
                {regions.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>

            {/* Time Bucket Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label htmlFor="time-bucket-filter" style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Time Bucket:
              </label>
              <select
                id="time-bucket-filter"
                data-testid="time-bucket-select"
                value={selectedTimeBucket ?? ''}
                onChange={(e) => setSelectedTimeBucket(Number(e.target.value))}
                style={{
                  padding: '6px 10px',
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid #475569',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '0.75rem',
                  fontFamily: 'monospace',
                  cursor: 'pointer',
                }}
              >
                {timeBuckets.map((tb) => (
                  <option key={tb} value={tb}>
                    {new Date(tb * 1000).toISOString().slice(0, 16).replace('T', ' ')} UTC ({tb})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Map + Cell Detail Split Workspace */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedCell ? '1fr 340px' : '1fr', gap: '20px' }}>
        {/* Map Container */}
        <div
          className="glass-panel"
          style={{
            position: 'relative',
            height: '620px',
            borderRadius: '12px',
            overflow: 'hidden',
          }}
        >
          <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

          {/* Legend Overlay */}
          <div
            style={{
              position: 'absolute',
              bottom: '16px',
              left: '16px',
              backgroundColor: 'rgba(11, 17, 32, 0.92)',
              border: '1px solid #334155',
              borderRadius: '8px',
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              fontSize: '0.75rem',
              zIndex: 20,
            }}
          >
            <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '2px' }}>Operational Tiers</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '14px', height: '14px', backgroundColor: '#f59e0b', borderRadius: '3px', border: '1px solid #fbbf24' }} />
              <span style={{ color: '#cbd5e1' }}><code>jamming_degraded</code> (Interference)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '14px', height: '14px', backgroundColor: '#8b5cf6', borderRadius: '3px', border: '1px solid #a855f7' }} />
              <span style={{ color: '#cbd5e1' }}><code>insufficient</code> (Abstained / Starvation)</span>
            </div>
            <div style={{ fontSize: '0.6875rem', color: '#94a3b8', marginTop: '4px' }}>
              Click any cell to inspect aircraft count &amp; reasons.
            </div>
          </div>

          {loadingCells && (
            <div
              style={{
                position: 'absolute',
                top: '16px',
                left: '16px',
                padding: '6px 12px',
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '6px',
                border: '1px solid #38bdf8',
                color: '#38bdf8',
                fontSize: '0.75rem',
                fontWeight: 600,
                zIndex: 20,
              }}
            >
              Loading cells for selected filter...
            </div>
          )}
        </div>

        {/* Selected Cell Detail Inspector */}
        {selectedCell && (
          <div
            className="glass-panel"
            data-testid="cell-detail-inspector"
            style={{
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              maxHeight: '620px',
              overflowY: 'auto',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <MapPin size={18} style={{ color: '#38bdf8' }} aria-hidden="true" />
                  <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
                    Cell Inspection
                  </h2>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedCell(null)}
                  style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
                  aria-label="Close inspector"
                >
                  <X size={16} />
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <span style={{ fontSize: '0.6875rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600 }}>
                    H3 Cell Index
                  </span>
                  <div data-testid="inspected-cell-id" style={{ fontSize: '0.875rem', fontFamily: 'monospace', color: '#38bdf8', marginTop: '2px' }}>
                    {selectedCell.h3_cell}
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.6875rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600 }}>
                    Evidence Tier
                  </span>
                  <div style={{ marginTop: '4px' }}>
                    <span
                      data-testid="inspected-cell-status"
                      style={{
                        display: 'inline-block',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        fontFamily: 'monospace',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        backgroundColor: selectedCell.status === 'jamming_degraded' ? 'rgba(251, 191, 36, 0.2)' : 'rgba(168, 85, 247, 0.2)',
                        color: selectedCell.status === 'jamming_degraded' ? '#fbbf24' : '#a855f7',
                        border: `1px solid ${selectedCell.status === 'jamming_degraded' ? 'rgba(251, 191, 36, 0.4)' : 'rgba(168, 85, 247, 0.4)'}`,
                      }}
                    >
                      {selectedCell.status}
                    </span>
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.6875rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600 }}>
                    Aircraft Count
                  </span>
                  <div data-testid="inspected-cell-aircraft-count" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', marginTop: '2px' }}>
                    {selectedCell.n_aircraft} {selectedCell.n_aircraft === 1 ? 'aircraft' : 'aircraft'}
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.6875rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600 }}>
                    Region
                  </span>
                  <div style={{ fontSize: '0.875rem', color: '#cbd5e1', marginTop: '2px' }}>
                    {selectedCell.region}
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.6875rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600 }}>
                    Primary Operational Reasons
                  </span>
                  <div data-testid="inspected-cell-reasons" style={{ marginTop: '4px' }}>
                    {selectedCell.reasons.length > 0 ? (
                      <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.75rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                        {selectedCell.reasons.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Standard regional telemetry threshold</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div style={{ borderTop: '1px solid #334155', paddingTop: '12px', marginTop: '16px', fontSize: '0.6875rem', color: '#94a3b8' }}>
              Time Bucket Epoch: {selectedCell.time_bucket}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
