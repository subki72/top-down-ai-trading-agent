import os
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Retrieve API Keys and Tokens
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================
# 3. TRADING SYSTEM CONFIGURATION
# ==========================================
SYMBOL = 'BTC/USDT'
LIMIT_CANDLES = 100

# Top-Down Analysis Timeframes
TF_MACRO = '1h'    # For Trend Agent
TF_MICRO = '15m'   # For Pattern Agent
TF_TRIGGER = '5m'  # For Sniper/Trigger Agent

# ==========================================
# 4. GUARDRAILS / RISK MANAGEMENT CONFIGURATION
# ==========================================
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70