import requests
from datetime import datetime, timezone, timedelta

def fetch_crypto_news(hours_back=24):
    """
    Fetch crypto news from CryptoCompare API (FREE, no API key required).
    Endpoint: https://min-api.cryptocompare.com/data/v2/news/
    
    Returns list of raw articles:
    [{"title", "source", "url", "published_at", "body", "categories"}]
    """
    print(f"[NEWS_FETCHER] Fetching crypto news from last {hours_back} hours via CryptoCompare...")
    
    base_url = "https://min-api.cryptocompare.com/data/v2/news/"
    params = {
        "lang": "EN",
        "sortOrder": "latest"
    }
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    cutoff_ts = int(cutoff_time.timestamp())
    
    articles = []
    
    try:
        # CryptoCompare returns ~50 articles per call, paginate with lTs
        last_timestamp = None
        max_pages = 5  # Safety limit
        
        for page in range(max_pages):
            if last_timestamp:
                params["lTs"] = last_timestamp
            
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") != "Success":
                print(f"[NEWS_FETCHER] API error: {data.get('Message', 'Unknown')}")
                break
            
            news_items = data.get("Data", [])
            if not news_items:
                break
            
            for item in news_items:
                published_ts = item.get("published_on", 0)
                
                # Stop if article is older than cutoff
                if published_ts < cutoff_ts:
                    print(f"[NEWS_FETCHER] Reached cutoff time, stopping pagination")
                    return articles
                
                published_at = datetime.fromtimestamp(published_ts, tz=timezone.utc).isoformat()
                
                # Extract categories from the tags field
                categories_raw = item.get("categories", "")
                categories = [c.strip() for c in categories_raw.split("|") if c.strip()]
                
                articles.append({
                    "title": item.get("title", ""),
                    "source": item.get("source_info", {}).get("name", item.get("source", "Unknown")),
                    "url": item.get("url", item.get("guid", "")),
                    "published_at": published_at,
                    "categories": categories,
                    "body": item.get("body", "")[:300]  # First 300 chars for context
                })
            
            # Set pagination cursor to oldest article in this batch
            last_timestamp = news_items[-1].get("published_on")
            
            # If we got fewer than expected, we've reached the end
            if len(news_items) < 20:
                break
        
        print(f"[NEWS_FETCHER] Fetched {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"[ERROR] News fetch failed: {str(e)}")
        return []
