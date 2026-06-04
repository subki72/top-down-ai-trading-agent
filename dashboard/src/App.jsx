import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { getSupabase, isSupabaseConfigured } from './lib/supabase'
import Login from './pages/Login'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import News from './pages/News'
import './index.css'

function ProtectedRoute({ session, children }) {
  if (!session) return <Navigate to="/login" replace />
  return children
}

function SetupNotice() {
  return (
    <div className="login-page">
      <div className="login-card glass-card">
        <div className="login-header">
          <div className="login-header-icon">⚙️</div>
          <h1>Setup Required</h1>
          <p>Configure your Supabase credentials</p>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          <p style={{ marginBottom: 12 }}>
            Create a <code style={{ color: 'var(--accent-cyan)' }}>.env</code> file in the{' '}
            <code style={{ color: 'var(--accent-cyan)' }}>dashboard/</code> folder with:
          </p>
          <div style={{ 
            background: 'var(--bg-tertiary)', padding: 16, borderRadius: 8, 
            fontFamily: 'JetBrains Mono, monospace', fontSize: '0.8rem', marginBottom: 16 
          }}>
            VITE_SUPABASE_URL=https://your-project.supabase.co<br/>
            VITE_SUPABASE_ANON_KEY=your-anon-key-here
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
            Then restart the dev server with{' '}
            <code style={{ color: 'var(--accent-cyan)' }}>npm run dev</code>
          </p>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      setLoading(false)
      return
    }

    const supabase = getSupabase()
    if (!supabase) {
      setLoading(false)
      return
    }

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    }).catch(() => {
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', background: '#0a0a0f'
      }}>
        <div className="spinner" style={{ width: 40, height: 40 }}></div>
      </div>
    )
  }

  if (!isSupabaseConfigured()) {
    return <SetupNotice />
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={session ? <Navigate to="/dashboard" replace /> : <Login />}
        />
        <Route
          element={
            <ProtectedRoute session={session}>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/news" element={<News />} />
        </Route>
        <Route path="*" element={<Navigate to={session ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  )
}
