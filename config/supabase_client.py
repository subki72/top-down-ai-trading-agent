from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY
from config.logger import setup_logger
from tools.resilience import retry_with_backoff

logger = setup_logger("supabase_client")

_client_instance: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """Initialize and return singleton Supabase client, or None if not configured."""
    global _client_instance
    if _client_instance is not None:
        return _client_instance

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("SUPABASE_URL or SUPABASE_KEY not configured.")
        return None

    try:
        _client_instance = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _client_instance
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
        return None

def insert_trading_signal(signal_data: Dict[str, Any]):
    """Insert a trading signal into the trading_signals table with retry."""
    client = get_supabase_client()
    if not client:
        logger.warning("Supabase client unavailable, skipping signal insert.")
        return None

    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def execute_insert():
        return client.table("trading_signals").insert(signal_data).execute()

    try:
        result = execute_insert()
        logger.info("Trading signal inserted successfully into Supabase")
        return result
    except Exception as e:
        logger.error(f"Failed to insert trading signal: {str(e)}", exc_info=True)
        return None

def insert_news_articles(articles: List[Dict[str, Any]]):
    """Batch insert categorized news articles into the crypto_news table with retry."""
    if not articles:
        return None

    client = get_supabase_client()
    if not client:
        logger.warning("Supabase client unavailable, skipping news insert.")
        return None

    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def execute_insert():
        return client.table("crypto_news").insert(articles).execute()

    try:
        result = execute_insert()
        logger.info(f"{len(articles)} news articles inserted successfully into Supabase")
        return result
    except Exception as e:
        logger.error(f"Failed to insert news articles: {str(e)}", exc_info=True)
        return None
