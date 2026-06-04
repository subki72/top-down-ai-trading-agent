import { useState } from 'react'
import { IconExpand, IconClose, IconTrendUp, IconTrendDown, IconTarget, IconShield, IconActivity, IconClock } from './Icons'

export default function SignalCard({ signal, index }) {
  const [expanded, setExpanded] = useState(false)

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

  const isBullish = signal.macro_trend?.toUpperCase() === 'BULLISH'
  const TrendIcon = isBullish ? IconTrendUp : IconTrendDown
  const trendColor = isBullish ? 'var(--sent-bullish)' : 'var(--sent-bearish)'

  return (
    <>
      <div
        className={`signal-card glass-card animate-in stagger-${(index % 4) + 1}`}
        onClick={() => setExpanded(true)}
        style={{ cursor: 'pointer' }}
      >
        <div className="signal-card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="signal-card-asset">{signal.asset_pair || 'N/A'}</span>
            <span className={getActionBadgeClass(signal.final_action)}>
              {signal.final_action || 'IDLE'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="signal-card-time">
              <IconClock size={12} color="var(--text-muted)" />
              {' '}{formatTime(signal.created_at)}
            </span>
            <button className="expand-btn" onClick={(e) => { e.stopPropagation(); setExpanded(true) }}>
              <IconExpand size={16} color="var(--text-muted)" />
            </button>
          </div>
        </div>

        <div className="signal-card-body">
          <div className="signal-metric">
            <span className="signal-metric-label">
              <TrendIcon size={12} color={trendColor} /> H1 Trend
            </span>
            <span className={getTrendBadgeClass(signal.macro_trend)} style={{ width: 'fit-content' }}>
              {signal.macro_trend || '—'}
            </span>
          </div>
          <div className="signal-metric">
            <span className="signal-metric-label">
              <IconActivity size={12} color="var(--accent-cyan)" /> M15 Pattern
            </span>
            <span className="signal-metric-value">{truncate(signal.micro_signal, 40)}</span>
          </div>
          <div className="signal-metric">
            <span className="signal-metric-label">
              <IconShield size={12} color="var(--accent-purple)" /> Risk/Reward
            </span>
            <span className="signal-metric-value mono">
              {signal.rr_ratio ? `1:${signal.rr_ratio}` : '—'}
            </span>
          </div>
          <div className="signal-metric">
            <span className="signal-metric-label">
              <IconTarget size={12} color="var(--cat-macro)" /> Trigger
            </span>
            <span className="signal-metric-value">{truncate(signal.trigger_detail, 40)}</span>
          </div>
        </div>
      </div>

      {/* Expanded Modal */}
      {expanded && (
        <div className="modal-overlay" onClick={() => setExpanded(false)}>
          <div className="modal-content glass-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{ fontSize: '1.3rem', fontWeight: 800 }}>{signal.asset_pair || 'N/A'}</span>
                <span className={getActionBadgeClass(signal.final_action)}>
                  {signal.final_action || 'IDLE'}
                </span>
              </div>
              <button className="modal-close-btn" onClick={() => setExpanded(false)}>
                <IconClose size={22} />
              </button>
            </div>

            <div className="modal-timestamp">
              <IconClock size={14} color="var(--text-muted)" />
              {formatTime(signal.created_at)}
            </div>

            <div className="modal-grid">
              <div className="modal-section">
                <div className="modal-section-header">
                  <TrendIcon size={18} color={trendColor} />
                  <span>H1 Macro Trend</span>
                </div>
                <div className="modal-section-body">
                  <span className={getTrendBadgeClass(signal.macro_trend)} style={{ fontSize: '0.85rem', padding: '6px 16px' }}>
                    {signal.macro_trend || '—'}
                  </span>
                </div>
              </div>

              <div className="modal-section">
                <div className="modal-section-header">
                  <IconShield size={18} color="var(--accent-purple)" />
                  <span>Risk / Reward Ratio</span>
                </div>
                <div className="modal-section-body">
                  <span className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: signal.rr_ratio >= 1.5 ? 'var(--sent-bullish)' : 'var(--sent-bearish)' }}>
                    {signal.rr_ratio ? `1 : ${signal.rr_ratio}` : '—'}
                  </span>
                </div>
              </div>
            </div>

            <div className="modal-section modal-section-full">
              <div className="modal-section-header">
                <IconActivity size={18} color="var(--accent-cyan)" />
                <span>M15 Pattern Analysis</span>
              </div>
              <div className="modal-section-body">
                <p className="modal-detail-text">{signal.micro_signal || '—'}</p>
              </div>
            </div>

            <div className="modal-section modal-section-full">
              <div className="modal-section-header">
                <IconTarget size={18} color="var(--cat-macro)" />
                <span>M5 Trigger Detail</span>
              </div>
              <div className="modal-section-body">
                <p className="modal-detail-text">{signal.trigger_detail || '—'}</p>
              </div>
            </div>

            {signal.execution_logs && signal.execution_logs.length > 0 && (
              <div className="modal-section modal-section-full">
                <div className="modal-section-header">
                  <IconActivity size={18} color="var(--text-muted)" />
                  <span>Execution Logs</span>
                </div>
                <div className="modal-section-body">
                  <div className="modal-logs">
                    {signal.execution_logs.map((log, i) => (
                      <div key={i} className="modal-log-entry mono">{log}</div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}
