import os
from dotenv import load_dotenv

load_dotenv()

# API Keys and Security
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Global Trading Parameters
SYMBOL = os.getenv("COIN_SYMBOL", "TAO/USD")
EXCHANGE_ID = os.getenv("EXCHANGE_ID", "kraken")

# Timeframe Configuration & Dynamic Candle Limits
TF_MACRO = '1h'    
LIMIT_MACRO = 60 

TF_MICRO = '15m'   
LIMIT_MICRO = 20   

TF_TRIGGER = '5m'  
LIMIT_TRIGGER = 5 

# Technical Thresholds
MIN_RR_RATIO = float(os.getenv("MIN_RR_RATIO", "1.5"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30.0"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70.0"))

# Capital Management & Position Sizing Parameters
ACCOUNT_EQUITY = float(os.getenv("ACCOUNT_EQUITY", "10000.0"))  # USD balance
MAX_RISK_PER_TRADE_PCT = float(os.getenv("MAX_RISK_PER_TRADE_PCT", "1.0"))  # Risk 1.0% equity per trade
MAX_CAPITAL_ALLOCATION_PCT = float(os.getenv("MAX_CAPITAL_ALLOCATION_PCT", "25.0"))  # Max 25% balance per trade
DEFAULT_LEVERAGE = float(os.getenv("DEFAULT_LEVERAGE", "1.0"))

# Network, Retries & Timeouts
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_INITIAL_DELAY = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))

# LLM Models Configuration
MODEL_STRATEGIST = os.getenv("MODEL_STRATEGIST", "llama-3.3-70b-versatile")
MODEL_ANALYST = os.getenv("MODEL_ANALYST", "llama-3.3-70b-versatile")
MODEL_SNIPER = os.getenv("MODEL_SNIPER", "llama-3.1-8b-instant")
MODEL_MANAGER = os.getenv("MODEL_MANAGER", "llama-3.1-8b-instant")
MODEL_NEWS = os.getenv("MODEL_NEWS", "llama-3.1-8b-instant")

def validate_environment(require_telegram: bool = False, require_supabase: bool = False) -> list[str]:
    """
    Validates essential environment variables and returns a list of missing ones.
    """
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if require_telegram:
        if not TELEGRAM_TOKEN:
            missing.append("TELEGRAM_TOKEN")
        if not TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
    if require_supabase:
        if not SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not SUPABASE_KEY:
            missing.append("SUPABASE_KEY")
    return missing