import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

const navigation = [
  { path: '/dashboard', label: 'Dashboard', icon: '🌌', badge: null },
  { path: '/map', label: 'Live Disaster Map', icon: '🗺️', badge: 'LIVE' },
  { path: '/incidents', label: 'Incidents Registry', icon: '🚨', badge: null },
  { path: '/allocations', label: 'Resource Allocation', icon: '⚖️', badge: null },
  { path: '/missions', label: 'Rescue Missions', icon: '🚁', badge: null },
  { path: '/personnel', label: 'Field Personnel', icon: '👥', badge: null },
  { path: '/predictions', label: 'AI Demand Forecast', icon: '📈', badge: 'AI' },
  { path: '/resources', label: 'Inventory Depots', icon: '📦', badge: null },
  { path: '/reports', label: 'Intelligence Reports', icon: '📋', badge: null },
  { path: '/settings', label: 'Telemetry & Feeds', icon: '⚙️', badge: null },
];

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false); // Mobile drawer open
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false); // Desktop collapse
  const [isMobile, setIsMobile] = useState(() => typeof window !== 'undefined' ? window.innerWidth <= 1024 : false);
  const [currentTime, setCurrentTime] = useState(new Date().toUTCString());
  const location = useLocation();

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 1024;
      setIsMobile(mobile);
      if (!mobile) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toUTCString().replace('GMT', 'UTC'));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const currentNav = navigation.find(n => location.pathname.startsWith(n.path));

  const toggleSidebar = () => {
    if (isMobile) {
      setSidebarOpen(prev => !prev);
    } else {
      setSidebarCollapsed(prev => !prev);
    }
  };

  const closeMobileSidebar = () => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  return (
    <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''} ${sidebarOpen ? 'mobile-sidebar-open' : ''}`}>
      {/* Cosmic Sidebar */}
      <aside className="cosmic-sidebar">
        {/* Brand / Logo Section */}
        <div style={{ padding: 'var(--spacing-lg) var(--spacing-md)', borderBottom: '1px solid rgba(0, 242, 254, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
            <div
              style={{
                width: 38,
                height: 38,
                background: 'linear-gradient(135deg, #00f2fe 0%, #7928ca 100%)',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#050814',
                fontWeight: '900',
                fontSize: '18px',
                boxShadow: '0 0 16px rgba(0, 242, 254, 0.5)',
                position: 'relative',
              }}
            >
              ⚡
            </div>
            <div>
              <div style={{ fontSize: '15px', fontWeight: '800', letterSpacing: '0.6px', color: '#ffffff' }}>
                A.E.G.I.S. COSMIC
              </div>
              <div style={{ fontSize: '10px', color: 'var(--color-cyan)', textTransform: 'uppercase', letterSpacing: '1.2px', fontWeight: '700' }}>
                Emergency Intelligence
              </div>
            </div>
          </div>
          {isMobile && (
            <button
              onClick={closeMobileSidebar}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--color-text-muted)',
                fontSize: '18px',
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
              }}
              title="Close Navigation"
            >
              ✕
            </button>
          )}
        </div>

        <div style={{ padding: '0 var(--spacing-md) var(--spacing-sm)' }}>
          <div
            style={{
              marginTop: 'var(--spacing-sm)',
              fontSize: '10.5px',
              padding: '4px 8px',
              background: 'rgba(0, 242, 254, 0.08)',
              border: '1px solid rgba(0, 242, 254, 0.2)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-cyan)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span className="pulse-dot" style={{ background: '#05ffa1' }}></span>
            <span>Orbital Operations Center</span>
          </div>
        </div>

        {/* Navigation links */}
        <nav style={{ flex: 1, padding: 'var(--spacing-md) var(--spacing-sm)' }}>
          <ul style={{ listStyle: 'none' }}>
            {navigation.map((item) => (
              <li key={item.path} style={{ marginBottom: '4px' }}>
                <NavLink
                  to={item.path}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '9px 14px',
                    borderRadius: 'var(--radius-md)',
                    color: isActive ? '#ffffff' : 'var(--color-text-muted)',
                    background: isActive 
                      ? 'linear-gradient(90deg, rgba(0, 242, 254, 0.16) 0%, rgba(157, 78, 221, 0.14) 100%)' 
                      : 'transparent',
                    border: isActive ? '1px solid rgba(0, 242, 254, 0.4)' : '1px solid transparent',
                    boxShadow: isActive ? '0 0 14px rgba(0, 242, 254, 0.2)' : 'none',
                    fontWeight: isActive ? '600' : '500',
                    fontSize: '13.5px',
                    textDecoration: 'none',
                    transition: 'all 0.2s ease',
                  })}
                  onClick={closeMobileSidebar}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <span style={{ fontSize: '17px' }}>{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      style={{
                        fontSize: '9.5px',
                        fontWeight: '800',
                        padding: '2px 6px',
                        borderRadius: 'var(--radius-full)',
                        background: item.badge === 'LIVE' ? 'rgba(255, 42, 109, 0.25)' : 'rgba(0, 242, 254, 0.2)',
                        color: item.badge === 'LIVE' ? '#ff3b77' : '#00f2fe',
                        border: `1px solid ${item.badge === 'LIVE' ? 'rgba(255, 42, 109, 0.5)' : 'rgba(0, 242, 254, 0.4)'}`,
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Quick Launch footer */}
        <div style={{ padding: 'var(--spacing-md)', borderTop: '1px solid rgba(0, 242, 254, 0.12)' }}>
          <NavLink
            to="/incidents"
            className="btn btn-primary"
            style={{
              width: '100%',
              textDecoration: 'none',
              padding: '10px 14px',
              fontSize: '13px',
            }}
            onClick={closeMobileSidebar}
          >
            <span>+</span> Declare Incident
          </NavLink>
        </div>
      </aside>

      {/* Sidebar mobile overlay */}
      <div
        className="sidebar-overlay"
        onClick={closeMobileSidebar}
      />

      {/* Main Content Area */}
      <div className="main-content-wrapper">
        {/* Cosmic Topbar Header */}
        <header
          style={{
            height: 'var(--header-height)',
            background: 'rgba(7, 12, 36, 0.75)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(0, 242, 254, 0.16)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 var(--spacing-lg)',
            position: 'sticky',
            top: 0,
            zIndex: 50,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
            <button
              onClick={toggleSidebar}
              className="sidebar-toggle-btn"
              title={sidebarCollapsed ? "Expand Navigation" : "Collapse Navigation"}
              aria-label="Toggle navigation menu"
            >
              ☰
            </button>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                <span style={{ fontSize: '18px' }}>{currentNav?.icon || '🛸'}</span>
                <h1 style={{ fontSize: '18px', fontWeight: '700', color: '#ffffff', letterSpacing: '0.2px' }}>
                  {currentNav?.label || 'Cosmic Telemetry'}
                </h1>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
            {/* Real-time Clock */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '11.5px',
                color: 'var(--color-text-muted)',
                background: 'rgba(0, 242, 254, 0.05)',
                padding: '5px 12px',
                borderRadius: 'var(--radius-full)',
                border: '1px solid rgba(0, 242, 254, 0.15)',
                fontFamily: 'var(--font-mono)',
              }}
              className="header-clock"
            >
              <span className="pulse-dot" style={{ background: '#00f2fe' }}></span>
              <span>{currentTime}</span>
            </div>

            {/* System Status Pill */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '11px',
                fontWeight: '700',
                color: '#05ffa1',
                background: 'rgba(5, 255, 161, 0.1)',
                padding: '5px 12px',
                borderRadius: 'var(--radius-full)',
                border: '1px solid rgba(5, 255, 161, 0.3)',
              }}
            >
              <span className="pulse-dot" style={{ background: '#05ffa1' }}></span>
              <span>LINKED</span>
            </div>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="main-viewport">
          <div className="content-container">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
