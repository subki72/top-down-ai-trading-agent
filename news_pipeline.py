import os
import sys
from config.settings import GROQ_API_KEY, validate_environment
from tools.news_fetcher import fetch_crypto_news
from agents.news_classifier_agent import classify_news_batch
from config.supabase_client import insert_news_articles
from config.logger import setup_logger

logger = setup_logger("news_pipeline")

def run_news_pipeline():
    """
    Daily news pipeline entry point.
    Fetches last 24 hours of crypto news, classifies with AI, 
    and stores in Supabase for the web dashboard.
    """
    logger.info("=== STARTING AI CRYPTO NEWS PIPELINE ===")

    # Startup validation
    missing = validate_environment(require_telegram=False, require_supabase=False)
    if "GROQ_API_KEY" in missing:
        logger.critical("Startup aborted! GROQ_API_KEY is not configured.")
        sys.exit(1)
    
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

    # Step 1: Fetch news from last 24 hours
    logger.info("[STEP 1] Fetching crypto news via RSS...")
    raw_articles = fetch_crypto_news(hours_back=24)
    
    if not raw_articles:
        logger.warning("[PIPELINE] No articles found from the past 24 hours. Exiting cleanly.")
        sys.exit(0)
    
    logger.info(f"[PIPELINE] Collected {len(raw_articles)} raw news items")
    
    # Step 2: Classify with AI
    logger.info("[STEP 2] Classifying articles with LLM...")
    classified_articles = classify_news_batch(raw_articles)
    
    if not classified_articles:
        logger.error("[PIPELINE] Classification returned empty list. Exiting.")
        sys.exit(1)
    
    # Step 3: Insert into Supabase
    logger.info("[STEP 3] Persisting categorized news into Supabase...")
    result = insert_news_articles(classified_articles)
    
    # Summary Metrics
    categories = {}
    sentiments = {}
    for article in classified_articles:
        cat = article.get("category", "UNKNOWN")
        sent = article.get("sentiment", "UNKNOWN")
        categories[cat] = categories.get(cat, 0) + 1
        sentiments[sent] = sentiments.get(sent, 0) + 1
    
    logger.info("=" * 50)
    logger.info("NEWS PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"Total articles processed: {len(classified_articles)}")
    logger.info(f"Breakdown by Category: {categories}")
    logger.info(f"Breakdown by Sentiment: {sentiments}")
    logger.info("=" * 50)

if __name__ == "__main__":
    run_news_pipeline()
