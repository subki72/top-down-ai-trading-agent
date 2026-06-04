import { NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'
import { IconBot, IconSignal, IconNews, IconMenu, IconClose } from './Icons'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <>
      {/* Mobile Header */}
      <div className="mobile-header">
        <button className="mobile-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <IconClose size={22} /> : <IconMenu size={22} />}
        </button>
        <span className="gradient-text" style={{ fontWeight: 700, fontSize: '1rem' }}>AI Trading Bot</span>
        <div style={{ width: 32 }}></div>
      </div>

      <div className="app-layout">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <IconBot size={22} color="#fff" />
            </div>
            <div>
              <h1>AI Trading</h1>
              <span>Command Center</span>
            </div>
          </div>

          <nav className="sidebar-nav">
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <span className="nav-link-icon"><IconSignal size={18} /></span>
              Trading Signals
            </NavLink>
            <NavLink
              to="/news"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <span className="nav-link-icon"><IconNews size={18} /></span>
              AI News Feed
            </NavLink>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <Outlet />
        </main>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
            zIndex: 99
          }}
        />
      )}
    </>
  )
}
