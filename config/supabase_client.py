import os
from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_trading_signal(signal_data: dict):
    """Insert a trading signal into the trading_signals table."""
    try:
        client = get_supabase_client()
        result = client.table("trading_signals").insert(signal_data).execute()
        print(f"[SUPABASE] Trading signal inserted successfully")
        return result
    except Exception as e:
        print(f"[SUPABASE_ERROR] Failed to insert trading signal: {str(e)}")
        return None

def insert_news_articles(articles: list):
    """Batch insert categorized news articles into the crypto_news table."""
    try:
        client = get_supabase_client()
        result = client.table("crypto_news").insert(articles).execute()
        print(f"[SUPABASE] {len(articles)} news articles inserted successfully")
        return result
    except Exception as e:
        print(f"[SUPABASE_ERROR] Failed to insert news articles: {str(e)}")
        return None
