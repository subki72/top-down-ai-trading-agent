export default function NewsCard({ article, index }) {
  const getCategoryBadge = (category) => {
    switch (category) {
      case 'TECHNICAL':
        return { className: 'badge badge-technical', label: '🔧 Teknikal' }
      case 'FUNDAMENTAL_MACRO':
        return { className: 'badge badge-macro', label: '🌍 Makro' }
      case 'FUNDAMENTAL_ONCHAIN':
        return { className: 'badge badge-onchain', label: '⛓️ Onchain' }
      default:
        return { className: 'badge badge-neutral', label: category || 'Unknown' }
    }
  }

  const getSentimentBadge = (sentiment) => {
    switch (sentiment) {
      case 'BULLISH':
        return { className: 'badge badge-bullish', label: '↑ Bullish' }
      case 'BEARISH':
        return { className: 'badge badge-bearish', label: '↓ Bearish' }
      default:
        return { className: 'badge badge-neutral', label: '→ Neutral' }
    }
  }

  const formatTime = (dateStr) => {
    if (!dateStr) return '—'
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now - d
    const diffHrs = Math.floor(diffMs / (1000 * 60 * 60))
    const diffMins = Math.floor(diffMs / (1000 * 60))

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHrs < 24) return `${diffHrs}h ago`
    return d.toLocaleDateString('id-ID', {
      day: '2-digit', month: 'short',
      timeZone: 'Asia/Jakarta'
    })
  }

  const cat = getCategoryBadge(article.category)
  const sent = getSentimentBadge(article.sentiment)

  return (
    <div className={`news-card glass-card animate-in stagger-${(index % 4) + 1}`}>
      <div className="news-card-header">
        <span className={cat.className}>{cat.label}</span>
        <span className={sent.className}>{sent.label}</span>
      </div>

      <h3 className="news-card-title">
        {article.url ? (
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
        ) : (
          article.title
        )}
      </h3>

      {article.summary && article.summary !== article.title && (
        <p className="news-card-summary">{article.summary}</p>
      )}

      <div className="news-card-footer">
        <span className="news-card-source">{article.source || 'Unknown'}</span>
        <span className="news-card-time">{formatTime(article.published_at)}</span>
      </div>
    </div>
  )
}
