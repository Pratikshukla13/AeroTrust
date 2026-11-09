import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapPin, Layers, Radio } from 'lucide-react'

export default function MapPage() {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  useEffect(() => {
    if (!mapContainerRef.current) return

    // Fully offline vector style using local Natural Earth GeoJSON stored in /public/data
    const offlineStyle: maplibregl.StyleSpecification = {
      version: 8,
      name: 'AeroTrust Offline Aerospace Vector',
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
      center: [25.0, 48.0], // Centered over Europe / Mediterranean / Baltic
      zoom: 3.2,
      maxZoom: 9,
      minZoom: 1.5,
      attributionControl: false,
    })

    map.addControl(
      new maplibregl.NavigationControl({ showCompass: true }),
      'top-right'
    )

    map.on('load', () => {
      setMapLoaded(true)
    })

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Panel */}
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 'var(--text-xl)', fontWeight: 700, color: '#f8fafc' }}>
              Interference Observatory Map
            </h2>
            <p style={{ margin: '4px 0 0', fontSize: 'var(--text-sm)', color: '#94a3b8' }}>
              Offline MapLibre GL instance powered by local Natural Earth vectors. Zero external tile servers.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '6px',
                backgroundColor: 'rgba(56, 189, 248, 0.12)',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                color: '#38bdf8',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
              }}
            >
              <Radio size={14} aria-hidden="true" />
              {mapLoaded ? 'Base Map Loaded' : 'Initializing Offline Vectors...'}
            </span>
          </div>
        </div>
      </div>

      {/* Map Canvas Glass Container */}
      <div
        className="glass-panel"
        style={{
          position: 'relative',
          height: '580px',
          overflow: 'hidden',
          borderRadius: '12px',
        }}
      >
        <div
          ref={mapContainerRef}
          data-testid="maplibre-container"
          style={{ width: '100%', height: '100%' }}
        />

        {/* Legend / Overlay Controls (High contrast) */}
        <div
          style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            border: '1px solid #334155',
            borderRadius: '8px',
            padding: '12px 16px',
            fontSize: 'var(--text-xs)',
            color: '#f8fafc',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            zIndex: 10,
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={14} style={{ color: '#38bdf8' }} aria-hidden="true" />
            <span>Map Layers & Sources</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#131c2e', border: '1px solid #2a3a55', borderRadius: '2px' }} />
              <span style={{ color: '#cbd5e1' }}>Natural Earth 110m (Local GeoJSON)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: 'rgba(244, 63, 94, 0.4)', border: '1px solid #f43f5e', borderRadius: '2px' }} />
              <span style={{ color: '#cbd5e1' }}>H3 Regional Interference Cells (Coarse Res 5)</span>
            </div>
          </div>
        </div>

        {/* Region Quick Navigator */}
        <div
          style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            display: 'flex',
            gap: '8px',
            zIndex: 10,
          }}
        >
          {['Baltic', 'East Med', 'Black Sea'].map((reg) => (
            <button
              key={reg}
              onClick={() => {
                if (!mapRef.current) return
                if (reg === 'Baltic') mapRef.current.flyTo({ center: [21.5, 57.5], zoom: 4.8 })
                if (reg === 'East Med') mapRef.current.flyTo({ center: [33.5, 34.5], zoom: 5.0 })
                if (reg === 'Black Sea') mapRef.current.flyTo({ center: [35.0, 43.5], zoom: 4.8 })
              }}
              style={{
                backgroundColor: 'rgba(15, 23, 42, 0.88)',
                color: '#f8fafc',
                border: '1px solid #475569',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <MapPin size={12} style={{ color: '#38bdf8' }} aria-hidden="true" />
              {reg}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
