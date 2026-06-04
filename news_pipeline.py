import os
import sys
from config.settings import GROQ_API_KEY
from tools.news_fetcher import fetch_crypto_news
from agents.news_classifier_agent import classify_news_batch
from config.supabase_client import insert_news_articles

def run_news_pipeline():
    """
    Daily news pipeline entry point.
    Fetches last 24 hours of crypto news, classifies with AI, 
    and stores in Supabase for the web dashboard.
    
    Designed to run via GitHub Actions cron at 01:00 UTC (08:00 WIB).
    """
    # Validate required environment variables
    if not GROQ_API_KEY:
        print("[FATAL] GROQ_API_KEY not set!")
        sys.exit(1)
    
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    
    print("=" * 50)
    print("AI CRYPTO NEWS PIPELINE")
    print("=" * 50)
    
    # Step 1: Fetch news from last 24 hours
    print("\n[STEP 1] Fetching crypto news...")
    raw_articles = fetch_crypto_news(hours_back=24)
    
    if not raw_articles:
        print("[PIPELINE] No articles found. This may indicate an issue.")
        sys.exit(0)  # Not an error, just no news
    
    print(f"[PIPELINE] Found {len(raw_articles)} raw articles")
    
    # Step 2: Classify with AI
    print("\n[STEP 2] Classifying articles with AI...")
    classified_articles = classify_news_batch(raw_articles)
    
    if not classified_articles:
        print("[PIPELINE] Classification returned empty. Exiting.")
        sys.exit(1)
    
    # Step 3: Insert into Supabase
    print("\n[STEP 3] Storing in Supabase...")
    result = insert_news_articles(classified_articles)
    
    if not result:
        print("[FATAL] Failed to insert articles into Supabase!")
        sys.exit(1)
    
    # Summary
    categories = {}
    sentiments = {}
    for article in classified_articles:
        cat = article.get("category", "UNKNOWN")
        sent = article.get("sentiment", "UNKNOWN")
        categories[cat] = categories.get(cat, 0) + 1
        sentiments[sent] = sentiments.get(sent, 0) + 1
    
    print("\n" + "=" * 50)
    print("PIPELINE COMPLETE")
    print(f"Total articles processed: {len(classified_articles)}")
    print(f"Categories: {categories}")
    print(f"Sentiments: {sentiments}")
    print("=" * 50)

if __name__ == "__main__":
    run_news_pipeline()
