import { useState, useEffect } from 'react'
import { getSupabase } from '../lib/supabase'
import NewsCard from '../components/NewsCard'
import { IconNews, IconWrench, IconGlobe, IconChain, IconFilter } from '../components/Icons'

const CATEGORIES = [
  { key: 'ALL', label: 'All', icon: IconFilter },
  { key: 'TECHNICAL', label: 'Teknikal', icon: IconWrench },
  { key: 'FUNDAMENTAL_MACRO', label: 'Makro', icon: IconGlobe },
  { key: 'FUNDAMENTAL_ONCHAIN', label: 'Onchain', icon: IconChain }
]

export default function News() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('ALL')
  const [stats, setStats] = useState({ total: 0, technical: 0, macro: 0, onchain: 0 })

  useEffect(() => {
    const supabase = getSupabase()
    if (!supabase) { setLoading(false); return }

    fetchNews(supabase)

    // Real-time subscription for new news
    const channel = supabase
      .channel('crypto_news_realtime')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'crypto_news'
      }, (payload) => {
        setArticles(prev => [payload.new, ...prev])
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const fetchNews = async (supabase) => {
    try {
      const { data, error } = await supabase
        .from('crypto_news')
        .select('*')
        .order('published_at', { ascending: false })
        .limit(100)

      if (error) throw error
      setArticles(data || [])
      computeStats(data || [])
    } catch (err) {
      console.error('Error fetching news:', err)
    } finally {
      setLoading(false)
    }
  }

  const computeStats = (data) => {
    setStats({
      total: data.length,
      technical: data.filter(a => a.category === 'TECHNICAL').length,
      macro: data.filter(a => a.category === 'FUNDAMENTAL_MACRO').length,
      onchain: data.filter(a => a.category === 'FUNDAMENTAL_ONCHAIN').length
    })
  }

  const filteredArticles = activeFilter === 'ALL'
    ? articles
    : articles.filter(a => a.category === activeFilter)

  return (
    <>
      <div className="page-header">
        <h2><IconNews size={24} color="var(--accent-cyan)" /> AI News Feed</h2>
        <p>Crypto news categorized by AI — updated daily at 08:00 WIB</p>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-card glass-card animate-in stagger-1">
          <div className="stat-value gradient-text">{stats.total}</div>
          <div className="stat-label"><IconNews size={12} /> Total Articles</div>
        </div>
        <div className="stat-card glass-card animate-in stagger-2">
          <div className="stat-value" style={{ color: 'var(--cat-technical)' }}>{stats.technical}</div>
          <div className="stat-label"><IconWrench size={12} color="var(--cat-technical)" /> Teknikal</div>
        </div>
        <div className="stat-card glass-card animate-in stagger-3">
          <div className="stat-value" style={{ color: 'var(--cat-macro)' }}>{stats.macro}</div>
          <div className="stat-label"><IconGlobe size={12} color="var(--cat-macro)" /> Makro</div>
        </div>
        <div className="stat-card glass-card animate-in stagger-4">
          <div className="stat-value" style={{ color: 'var(--cat-onchain)' }}>{stats.onchain}</div>
          <div className="stat-label"><IconChain size={12} color="var(--cat-onchain)" /> Onchain</div>
        </div>
      </div>

      {/* Category Filter Tabs */}
      <div className="filter-tabs">
        {CATEGORIES.map(cat => {
          const CatIcon = cat.icon
          return (
            <button
              key={cat.key}
              className={`btn btn-ghost ${activeFilter === cat.key ? 'active' : ''}`}
              onClick={() => setActiveFilter(cat.key)}
            >
              <CatIcon size={14} /> {cat.label}
            </button>
          )
        })}
      </div>

      {/* News Feed */}
      {loading ? (
        <div className="empty-state">
          <div className="spinner" style={{ margin: '0 auto', width: 32, height: 32 }}></div>
          <p style={{ marginTop: 16 }}>Loading news...</p>
        </div>
      ) : filteredArticles.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon"><IconNews size={48} color="var(--text-muted)" /></div>
          <p>No news articles yet.</p>
          <p style={{ marginTop: 4, fontSize: '0.8rem' }}>
            News will be fetched daily at 08:00 WIB.
          </p>
        </div>
      ) : (
        <div className="news-grid">
          {filteredArticles.map((article, i) => (
            <NewsCard key={article.id} article={article} index={i} />
          ))}
        </div>
      )}
    </>
  )
}
