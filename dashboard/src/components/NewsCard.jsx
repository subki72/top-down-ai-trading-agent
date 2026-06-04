import { IconWrench, IconGlobe, IconChain, IconTrendUp, IconTrendDown, IconActivity, IconExternalLink, IconClock } from './Icons'

export default function NewsCard({ article, index }) {
  const getCategoryBadge = (category) => {
    switch (category) {
      case 'TECHNICAL':
        return { className: 'badge badge-technical', label: 'Teknikal', Icon: IconWrench, color: 'var(--cat-technical)' }
      case 'FUNDAMENTAL_MACRO':
        return { className: 'badge badge-macro', label: 'Makro', Icon: IconGlobe, color: 'var(--cat-macro)' }
      case 'FUNDAMENTAL_ONCHAIN':
        return { className: 'badge badge-onchain', label: 'Onchain', Icon: IconChain, color: 'var(--cat-onchain)' }
      default:
        return { className: 'badge badge-neutral', label: category || 'Unknown', Icon: IconActivity, color: 'var(--text-muted)' }
    }
  }

  const getSentimentBadge = (sentiment) => {
    switch (sentiment) {
      case 'BULLISH':
        return { className: 'badge badge-bullish', label: 'Bullish', Icon: IconTrendUp }
      case 'BEARISH':
        return { className: 'badge badge-bearish', label: 'Bearish', Icon: IconTrendDown }
      default:
        return { className: 'badge badge-neutral', label: 'Neutral', Icon: IconActivity }
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
  const CatIcon = cat.Icon
  const SentIcon = sent.Icon

  return (
    <div className={`news-card glass-card animate-in stagger-${(index % 4) + 1}`}>
      <div className="news-card-header">
        <span className={cat.className}>
          <CatIcon size={12} color={cat.color} /> {cat.label}
        </span>
        <span className={sent.className}>
          <SentIcon size={12} /> {sent.label}
        </span>
      </div>

      <h3 className="news-card-title">
        {article.url ? (
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
            <IconExternalLink size={12} color="var(--text-muted)" style={{ marginLeft: 6, display: 'inline-block', verticalAlign: 'middle' }} />
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
        <span className="news-card-time">
          <IconClock size={11} color="var(--text-muted)" /> {formatTime(article.published_at)}
        </span>
      </div>
    </div>
  )
}
