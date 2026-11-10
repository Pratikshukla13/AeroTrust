import { useState, useEffect, lazy, Suspense } from 'react'
import SyntheticBanner from './components/SyntheticBanner'
import DatasetFingerprintBar, { DatasetFingerprintData } from './components/DatasetFingerprintBar'
import DatasetSelector, { DatasetMode } from './components/DatasetSelector'
import OverviewPage from './pages/OverviewPage'
import MapPage from './pages/MapPage'
import FlightDetailPage from './pages/FlightDetailPage'
import SARPage from './pages/SARPage'
import IncidentClockPage from './pages/IncidentClockPage'
import BriefingPage from './pages/BriefingPage'
import CorridorsPage from './pages/CorridorsPage'
import WatchlistPage from './pages/WatchlistPage'
import LimitationsPage from './pages/LimitationsPage'
import './styles/theme.css'

import {
  Activity,
  Map as MapIcon,
  Plane,
  ShieldAlert,
  Clock,
  FileText,
  Navigation,
  EyeOff,
  AlertOctagon,
  Menu,
  X,
  Tag,
} from 'lucide-react'

// Lazy-load EarthBackground so initial paint is fast
const EarthBackground = lazy(() => import('./components/EarthBackground'))

export type RouteId =
  | 'overview'
  | 'map'
  | 'flight-detail'
  | 'sar'
  | 'incident-clock'
  | 'briefing'
  | 'corridors'
  | 'watchlist'
  | 'limitations'

interface NavItem {
  id: RouteId
  label: string
  icon: typeof Activity
  badge?: string
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'map', label: 'Interference Map', icon: MapIcon },
  { id: 'flight-detail', label: 'Flight Detail', icon: Plane },
  { id: 'sar', label: 'SAR Metrics', icon: ShieldAlert },
  { id: 'limitations', label: 'Limitations', icon: AlertOctagon },
  { id: 'incident-clock', label: 'Incident Scenario Calculator', icon: Clock },
  { id: 'briefing', label: 'Briefing (planned, not in this release)', icon: FileText, badge: 'Planned, not in this release' },
  { id: 'corridors', label: 'Corridors', icon: Navigation, badge: 'Planned, not in this release' },
  { id: 'watchlist', label: 'Watchlist', icon: EyeOff, badge: 'Planned, not in this release' },
]

export default function App() {
  const [currentRoute, setCurrentRoute] = useState<RouteId>('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDataset, setActiveDataset] = useState<DatasetMode>('benchmark')
  const [metaFingerprints, setMetaFingerprints] = useState<Record<string, DatasetFingerprintData> | null>(null)
  const [releaseTag, setReleaseTag] = useState<string>('v0.3.2-verified')
  const [incidentNavLabel, setIncidentNavLabel] = useState<string>('Incident Scenario Calculator (sources pending)')

  useEffect(() => {
    fetch('/api/incident-cases')
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then((cases: any[]) => {
        const allVerified =
          Array.isArray(cases) &&
          cases.length > 0 &&
          cases.every((c) => c.source_url && c.verification_status === 'sourced' && c.url_status === 'verified by user')
        if (allVerified) {
          setIncidentNavLabel('Incident Scenario Calculator')
        } else {
          setIncidentNavLabel('Incident Scenario Calculator (sources pending)')
        }
      })
      .catch(() => {
        setIncidentNavLabel('Incident Scenario Calculator (sources pending)')
      })
  }, [])

  useEffect(() => {
    fetch('/api/meta')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.fingerprints) {
          setMetaFingerprints(data.fingerprints)
          if (data.tag) setReleaseTag(data.tag)
        }
      })
      .catch(() => {
        // Fallback default fingerprint
        setMetaFingerprints({
          benchmark: {
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
          rule_trigger_demo: {
            tag: 'v0.3.2-verified',
            name: 'Rule-Trigger Demo (Telemetry Degradation Audit)',
            seed: '9999',
            flights: 200,
            n_clean: 175,
            n_spoof: 25,
            n_jam: 0,
            config_hash: 'b6011043368eca73',
            primary_unit: 'demo flight',
          },
        })
      })
  }, [])

  const currentFingerprint = metaFingerprints ? metaFingerprints[activeDataset] : null

  const renderCurrentPage = () => {
    switch (currentRoute) {
      case 'overview':
        return <OverviewPage activeDataset={activeDataset} onNavigate={setCurrentRoute} />
      case 'map':
        return <MapPage />
      case 'flight-detail':
        return <FlightDetailPage />
      case 'sar':
        return <SARPage />
      case 'limitations':
        return <LimitationsPage />
      case 'incident-clock':
        return <IncidentClockPage />
      case 'briefing':
        return (
          <div>
            <div
              style={{
                marginBottom: '16px',
                padding: '12px 16px',
                borderRadius: '8px',
                backgroundColor: 'rgba(234, 179, 8, 0.12)',
                border: '1px solid rgba(234, 179, 8, 0.4)',
                color: '#fef08a',
                fontSize: 'var(--text-sm)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertOctagon size={16} aria-hidden="true" style={{ color: '#fbbf24' }} />
              <span><strong>Planned, not in this release:</strong> Briefing generator is scheduled for future milestones and is not part of the active v0.3.2 release.</span>
            </div>
            <BriefingPage />
          </div>
        )
      case 'corridors':
        return (
          <div>
            <div
              style={{
                marginBottom: '16px',
                padding: '12px 16px',
                borderRadius: '8px',
                backgroundColor: 'rgba(234, 179, 8, 0.12)',
                border: '1px solid rgba(234, 179, 8, 0.4)',
                color: '#fef08a',
                fontSize: 'var(--text-sm)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertOctagon size={16} aria-hidden="true" style={{ color: '#fbbf24' }} />
              <span><strong>Planned, not in this release:</strong> Flight corridor analyzer is scheduled for future milestones and is not part of the active v0.3.2 release.</span>
            </div>
            <CorridorsPage />
          </div>
        )
      case 'watchlist':
        return (
          <div>
            <div
              style={{
                marginBottom: '16px',
                padding: '12px 16px',
                borderRadius: '8px',
                backgroundColor: 'rgba(234, 179, 8, 0.12)',
                border: '1px solid rgba(234, 179, 8, 0.4)',
                color: '#fef08a',
                fontSize: 'var(--text-sm)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertOctagon size={16} aria-hidden="true" style={{ color: '#fbbf24' }} />
              <span><strong>Planned, not in this release:</strong> Tail watchlist is scheduled for future milestones and is not part of the active v0.3.2 release.</span>
            </div>
            <WatchlistPage />
          </div>
        )
      default:
        return <OverviewPage activeDataset={activeDataset} onNavigate={setCurrentRoute} />
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* 1. Earth Background Component */}
      <Suspense fallback={null}>
        <EarthBackground />
      </Suspense>

      {/* 2. Persistent Synthetic Banner */}
      <SyntheticBanner />

      {/* 3. Header Bar with Dataset Selector, Release Tag & Limitations Link */}
      <header
        style={{
          position: 'sticky',
          top: '38px',
          zIndex: 40,
          minHeight: 'var(--header-height)',
          backgroundColor: 'rgba(7, 11, 20, 0.9)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          borderBottom: '1px solid #1e293b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          padding: '8px 24px',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation Menu"
            style={{
              display: 'none',
              background: 'none',
              border: 'none',
              color: '#f8fafc',
              cursor: 'pointer',
              padding: '6px',
            }}
            className="mobile-menu-btn"
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
          <div
            onClick={() => setCurrentRoute('overview')}
            style={{ display: 'flex', alignItems: 'baseline', gap: '8px', cursor: 'pointer' }}
          >
            <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
              AeroTrust
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              Observatory
            </span>
          </div>
        </div>

        {/* Center / Right: Dataset Selector + Release Tag + Limitations quick-link */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          {/* Dataset Selector (Benchmark vs Rule-Trigger Demo) */}
          <DatasetSelector activeDataset={activeDataset} onChangeDataset={setActiveDataset} />

          {/* Release Tag Badge */}
          <div
            data-testid="header-tag-badge"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'rgba(56, 189, 248, 0.12)',
              border: '1px solid rgba(56, 189, 248, 0.35)',
              color: '#38bdf8',
              fontSize: '0.75rem',
              fontWeight: 700,
            }}
          >
            <Tag size={12} aria-hidden="true" />
            <span>Tag: {releaseTag}</span>
          </div>

          {/* Limitations Link (Explicitly required in the top bar) */}
          <button
            type="button"
            data-testid="topbar-limitations-link"
            onClick={() => setCurrentRoute('limitations')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '6px',
              backgroundColor: currentRoute === 'limitations' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(30, 41, 59, 0.8)',
              border: currentRoute === 'limitations' ? '1px solid #f87171' : '1px solid #475569',
              color: currentRoute === 'limitations' ? '#fca5a5' : '#cbd5e1',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <AlertOctagon size={13} aria-hidden="true" style={{ color: '#ef4444' }} />
            <span>Limitations</span>
          </button>
        </div>
      </header>

      {/* 4. Subheader: Dataset Fingerprint Bar on EVERY page (Enclosed in landmark region) */}
      <section aria-label="Dataset Metadata and Verification Fingerprint">
        <DatasetFingerprintBar fingerprint={currentFingerprint} tag={releaseTag} />
      </section>

      {/* 5. Main Application Workspace (Sidebar + Dynamic Page) */}
      <div style={{ display: 'flex', flex: 1, position: 'relative', zIndex: 45 }}>
        {/* Sidebar Navigation */}
        <nav
          aria-label="Main Navigation"
          style={{
            width: 'var(--sidebar-width)',
            backgroundColor: 'rgba(11, 17, 32, 0.9)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            borderRight: '1px solid #1e293b',
            padding: '20px 12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
          }}
          className={`sidebar-nav ${mobileMenuOpen ? 'mobile-open' : ''}`}
        >
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            const isActive = currentRoute === item.id
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentRoute(item.id)
                  setMobileMenuOpen(false)
                }}
                aria-current={isActive ? 'page' : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: isActive ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid transparent',
                  backgroundColor: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                  color: isActive ? '#f8fafc' : '#cbd5e1',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: 'var(--text-sm)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background-color 0.15s ease, color 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Icon size={17} style={{ color: isActive ? '#38bdf8' : '#94a3b8' }} aria-hidden="true" />
                  <span>{item.id === 'incident-clock' ? incidentNavLabel : item.label}</span>
                </div>
                {item.badge && (
                  <span
                    style={{
                      fontSize: '0.625rem',
                      fontWeight: 600,
                      padding: '2px 5px',
                      borderRadius: '4px',
                      whiteSpace: 'nowrap',
                      backgroundColor:
                        item.badge.includes('Planned')
                          ? 'rgba(245, 158, 11, 0.15)'
                          : item.badge === 'Private'
                          ? 'rgba(244, 63, 94, 0.2)'
                          : 'rgba(100, 116, 139, 0.3)',
                      color:
                        item.badge.includes('Planned')
                          ? '#fbbf24'
                          : item.badge === 'Private'
                          ? '#fda4af'
                          : '#cbd5e1',
                      border: `1px solid ${
                        item.badge.includes('Planned')
                          ? 'rgba(245, 158, 11, 0.4)'
                          : item.badge === 'Private'
                          ? 'rgba(244, 63, 94, 0.4)'
                          : 'rgba(100, 116, 139, 0.4)'
                      }`,
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Dynamic Route Content */}
        <main
          style={{
            flex: 1,
            padding: '24px 32px',
            maxWidth: '1360px',
            width: '100%',
            margin: '0 auto',
            minHeight: 'calc(100vh - var(--header-height) - var(--banner-height) - 34px)',
          }}
        >
          {renderCurrentPage()}
        </main>
      </div>

      {/* Global Application Footer */}
      <footer
        role="contentinfo"
        data-testid="app-footer"
        style={{
          borderTop: '1px solid rgba(148, 163, 184, 0.15)',
          padding: '16px 32px',
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '0.75rem',
          color: '#94a3b8',
          position: 'relative',
          zIndex: 40,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <span>
            Evaluation Tag:{' '}
            <strong data-testid="footer-eval-tag" style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
              v0.3.2-verified
            </strong>
          </span>
          <span style={{ color: '#475569' }}>|</span>
          <span>
            App Tag:{' '}
            <strong data-testid="footer-app-tag" style={{ color: '#a78bfa', fontFamily: 'monospace' }}>
              v1.0.3-demo
            </strong>
          </span>
        </div>
        <div data-testid="footer-disclaimer">
          Independent personal project, not affiliated with or endorsed by Airbus. Uses public information only.
        </div>
      </footer>

      <style>{`
        @media (max-width: 840px) {
          .mobile-menu-btn {
            display: block !important;
            position: relative;
            z-index: 70 !important;
          }
          .sidebar-nav {
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            z-index: 65 !important;
            padding-top: 140px !important;
            transform: translateX(-100%);
            transition: transform 0.2s ease-in-out;
            width: 280px !important;
            box-shadow: 4px 0 24px rgba(0,0,0,0.8);
          }
          .sidebar-nav.mobile-open {
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  )
}
