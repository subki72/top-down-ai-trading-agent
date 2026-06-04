export default function SignalCard({ signal, index }) {
  const getActionBadgeClass = (action) => {
    if (!action) return 'badge badge-idle'
    const a = action.toUpperCase()
    if (a.includes('EXECUTE')) return 'badge badge-execute'
    if (a.includes('REJECT') || a.includes('ERROR')) return 'badge badge-reject'
    return 'badge badge-idle'
  }

  const getTrendBadgeClass = (trend) => {
    if (!trend) return 'badge badge-neutral'
    const t = trend.toUpperCase()
    if (t === 'BULLISH') return 'badge badge-bullish'
    if (t === 'BEARISH') return 'badge badge-bearish'
    return 'badge badge-neutral'
  }

  const formatTime = (dateStr) => {
    if (!dateStr) return '—'
    const d = new Date(dateStr)
    return d.toLocaleString('id-ID', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
      timeZone: 'Asia/Jakarta'
    })
  }

  const truncate = (text, maxLen = 80) => {
    if (!text) return '—'
    return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
  }

  return (
    <div className={`signal-card glass-card animate-in stagger-${(index % 4) + 1}`}>
      <div className="signal-card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="signal-card-asset">{signal.asset_pair || 'N/A'}</span>
          <span className={getActionBadgeClass(signal.final_action)}>
            {signal.final_action || 'IDLE'}
          </span>
        </div>
        <span className="signal-card-time">{formatTime(signal.created_at)}</span>
      </div>

      <div className="signal-card-body">
        <div className="signal-metric">
          <span className="signal-metric-label">H1 Trend</span>
          <span className={getTrendBadgeClass(signal.macro_trend)} style={{ width: 'fit-content' }}>
            {signal.macro_trend || '—'}
          </span>
        </div>
        <div className="signal-metric">
          <span className="signal-metric-label">M15 Pattern</span>
          <span className="signal-metric-value">{truncate(signal.micro_signal, 40)}</span>
        </div>
        <div className="signal-metric">
          <span className="signal-metric-label">Risk/Reward</span>
          <span className="signal-metric-value mono">
            {signal.rr_ratio ? `1:${signal.rr_ratio}` : '—'}
          </span>
        </div>
        <div className="signal-metric">
          <span className="signal-metric-label">Trigger</span>
          <span className="signal-metric-value">{truncate(signal.trigger_detail, 40)}</span>
        </div>
      </div>
    </div>
  )
}
