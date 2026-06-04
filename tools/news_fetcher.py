import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# RSS feeds from major crypto news sources (100% free, no API key needed)
RSS_FEEDS = [
    {"url": "https://cointelegraph.com/rss", "source": "CoinTelegraph"},
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "source": "CoinDesk"},
    {"url": "https://decrypt.co/feed", "source": "Decrypt"},
    {"url": "https://bitcoinmagazine.com/feed", "source": "Bitcoin Magazine"},
    {"url": "https://thedefiant.io/feed", "source": "The Defiant"},
]

def _parse_rss_date(date_str):
    """Parse RSS date string to timezone-aware datetime."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        try:
            # Try ISO format as fallback
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

def _fetch_single_feed(feed_info, cutoff_time):
    """Fetch and parse a single RSS feed."""
    articles = []
    try:
        response = requests.get(
            feed_info["url"], 
            timeout=15,
            headers={"User-Agent": "AI-Trading-Bot/1.0"}
        )
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # Handle both RSS 2.0 and Atom feeds
        # RSS 2.0: channel/item
        items = root.findall(".//item")
        if not items:
            # Atom: entry
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//atom:entry", ns)
        
        for item in items:
            # RSS 2.0 fields
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date_str = item.findtext("pubDate", "") or item.findtext("published", "")
            description = item.findtext("description", "")
            
            # Atom fallback
            if not title:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                title = item.findtext("atom:title", "", ns)
            if not link:
                link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                if link_elem is not None:
                    link = link_elem.get("href", "")
            if not pub_date_str:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                pub_date_str = item.findtext("atom:updated", "", ns)
            
            # Parse date
            published_dt = _parse_rss_date(pub_date_str)
            if not published_dt:
                continue
                
            # Make timezone-aware if naive
            if published_dt.tzinfo is None:
                published_dt = published_dt.replace(tzinfo=timezone.utc)
            
            # Skip articles older than cutoff
            if published_dt < cutoff_time:
                continue
            
            # Clean description (strip HTML tags roughly)
            body = description
            if body:
                import re
                body = re.sub(r'<[^>]+>', '', body)
                body = body[:300].strip()
            
            articles.append({
                "title": title.strip(),
                "source": feed_info["source"],
                "url": link.strip(),
                "published_at": published_dt.isoformat(),
                "categories": [],  # Will be classified by AI
                "body": body
            })
        
        print(f"[NEWS_FETCHER] {feed_info['source']}: {len(articles)} articles")
        
    except Exception as e:
        print(f"[NEWS_FETCHER] Error fetching {feed_info['source']}: {str(e)}")
    
    return articles

def fetch_crypto_news(hours_back=24):
    """
    Fetch crypto news from multiple RSS feeds (FREE, no API key needed).
    
    Sources: CoinTelegraph, CoinDesk, Decrypt, Bitcoin Magazine, The Defiant
    
    Returns list of articles:
    [{"title", "source", "url", "published_at", "body", "categories"}]
    """
    print(f"[NEWS_FETCHER] Fetching crypto news from last {hours_back} hours via RSS feeds...")
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    
    all_articles = []
    for feed in RSS_FEEDS:
        articles = _fetch_single_feed(feed, cutoff_time)
        all_articles.extend(articles)
    
    # Sort by published date (newest first)
    all_articles.sort(key=lambda a: a["published_at"], reverse=True)
    
    # Remove duplicates by title similarity
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title_key = article["title"].lower()[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_articles.append(article)
    
    print(f"[NEWS_FETCHER] Total: {len(unique_articles)} unique articles from {len(RSS_FEEDS)} sources")
    return unique_articles
