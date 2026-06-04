import { useState, useEffect } from 'react'
import { getSupabase } from '../lib/supabase'
import SignalCard from '../components/SignalCard'

export default function Dashboard() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ total: 0, executes: 0, rejects: 0, lastUpdate: null })

  useEffect(() => {
    const supabase = getSupabase()
    if (!supabase) { setLoading(false); return }

    fetchSignals(supabase)
    
    // Real-time subscription
    const channel = supabase
      .channel('trading_signals_realtime')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'trading_signals'
      }, (payload) => {
        setSignals(prev => {
          const updated = [payload.new, ...prev]
          updateStats(updated)
          return updated
        })
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const fetchSignals = async (supabase) => {
    try {
      const { data, error } = await supabase
        .from('trading_signals')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)

      if (error) throw error
      setSignals(data || [])
      updateStats(data || [])
    } catch (err) {
      console.error('Error fetching signals:', err)
    } finally {
      setLoading(false)
    }
  }

  const updateStats = (data) => {
    const total = data.length
    const executes = data.filter(s => s.final_action?.includes('EXECUTE')).length
    const rejects = data.filter(s => s.final_action?.includes('REJECT')).length
    const lastUpdate = data.length > 0 ? data[0].created_at : null
    setStats({ total, executes, rejects, lastUpdate })
  }

  const formatLastUpdate = (dateStr) => {
    if (!dateStr) return 'No data yet'
    return new Date(dateStr).toLocaleString('id-ID', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
      timeZone: 'Asia/Jakarta'
    })
  }

  return (
    <>
      <div className="page-header">
        <h2>📊 Trading Signals</h2>
        <p>Real-time decisions from your AI trading firm</p>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-card glass-card animate-in stagger-1">
          <div className="stat-value gradient-text">{stats.total}</div>
          <div className="stat-label">Total Signals</div>
        </div>
        <div className="stat-card glass-card animate-in stagger-2">
          <div className="stat-value" style={{ color: 'var(--action-execute)' }}>{stats.executes}</div>
          <div className="stat-label">Executions</div>
        </div>
        <div className="stat-card glass-card animate-in stagger-3">
          <div className="stat-value" style={{ color: 'var(--action-reject)' }}>{stats.rejects}</div>
          <div className="stat-label">Rejections</div>
        </div>
        <div className="stat-card glass-card animate-in stagger-4">
          <div className="stat-value" style={{ color: 'var(--accent-cyan)', fontSize: '0.9rem', fontWeight: 600 }}>
            {formatLastUpdate(stats.lastUpdate)}
          </div>
          <div className="stat-label">Last Update</div>
        </div>
      </div>

      {/* Signal Feed */}
      {loading ? (
        <div className="empty-state">
          <div className="spinner" style={{ margin: '0 auto', width: 32, height: 32 }}></div>
          <p style={{ marginTop: 16 }}>Loading signals...</p>
        </div>
      ) : signals.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📡</div>
          <p>No trading signals yet.</p>
          <p style={{ marginTop: 4, fontSize: '0.8rem' }}>Signals will appear here when the bot runs.</p>
        </div>
      ) : (
        <div className="signal-grid">
          {signals.map((signal, i) => (
            <SignalCard key={signal.id} signal={signal} index={i} />
          ))}
        </div>
      )}
    </>
  )
}
