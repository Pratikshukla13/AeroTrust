import { useState, lazy, Suspense } from 'react'
import SyntheticBanner from './components/SyntheticBanner'
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
} from 'lucide-react'

// Lazy-load EarthBackground so initial paint of dashboard is never blocked
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
  { id: 'incident-clock', label: 'Incident Clock', icon: Clock },
  { id: 'briefing', label: 'Briefing', icon: FileText },
  { id: 'corridors', label: 'Corridors', icon: Navigation, badge: 'Stretch' },
  { id: 'watchlist', label: 'Watchlist', icon: EyeOff, badge: 'Private' },
  { id: 'limitations', label: 'Limitations', icon: AlertOctagon },
]

export default function App() {
  const [currentRoute, setCurrentRoute] = useState<RouteId>('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const renderCurrentPage = () => {
    switch (currentRoute) {
      case 'overview':
        return <OverviewPage />
      case 'map':
        return <MapPage />
      case 'flight-detail':
        return <FlightDetailPage />
      case 'sar':
        return <SARPage />
      case 'incident-clock':
        return <IncidentClockPage />
      case 'briefing':
        return <BriefingPage />
      case 'corridors':
        return <CorridorsPage />
      case 'watchlist':
        return <WatchlistPage />
      case 'limitations':
        return <LimitationsPage />
      default:
        return <OverviewPage />
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* 1. Full <EarthBackground/> Component (Lazy-loaded, replaces placeholder completely) */}
      <Suspense fallback={null}>
        <EarthBackground />
      </Suspense>

      {/* 2. Persistent Synthetic Banner */}
      <SyntheticBanner />

      {/* 3. Responsive Header Bar */}
      <header
        style={{
          position: 'sticky',
          top: '38px',
          zIndex: 40,
          height: 'var(--header-height)',
          backgroundColor: 'rgba(7, 11, 20, 0.85)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          borderBottom: '1px solid #1e293b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
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
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
              AeroTrust
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              Observatory
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#34d399', boxShadow: '0 0 8px #34d399' }} />
            <span style={{ fontSize: 'var(--text-xs)', color: '#cbd5e1', fontWeight: 500 }}>
              Fleet Telemetry Nominal
            </span>
          </div>
        </div>
      </header>

      {/* 4. Main Application Workspace (Sidebar + Content Area) */}
      <div style={{ display: 'flex', flex: 1, position: 'relative', zIndex: 10 }}>
        {/* Sidebar Navigation */}
        <nav
          aria-label="Main Navigation"
          style={{
            width: 'var(--sidebar-width)',
            backgroundColor: 'rgba(11, 17, 32, 0.85)',
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
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    style={{
                      fontSize: '0.6875rem',
                      fontWeight: 600,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: item.badge === 'Private' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(100, 116, 139, 0.3)',
                      color: item.badge === 'Private' ? '#fda4af' : '#cbd5e1',
                      border: `1px solid ${item.badge === 'Private' ? 'rgba(244, 63, 94, 0.4)' : 'rgba(100, 116, 139, 0.4)'}`,
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Dynamic Route Content (Resting on dark high-contrast glass panels) */}
        <main
          style={{
            flex: 1,
            padding: '24px 32px',
            maxWidth: '1360px',
            width: '100%',
            margin: '0 auto',
            minHeight: 'calc(100vh - var(--header-height) - var(--banner-height))',
          }}
        >
          {renderCurrentPage()}
        </main>
      </div>

      <style>{`
        @media (max-width: 840px) {
          .mobile-menu-btn {
            display: block !important;
          }
          .sidebar-nav {
            position: fixed;
            top: calc(var(--header-height) + var(--banner-height));
            left: 0;
            bottom: 0;
            z-index: 45;
            transform: translateX(-100%);
            transition: transform 0.2s ease-in-out;
            width: 260px !important;
          }
          .sidebar-nav.mobile-open {
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  )
}
