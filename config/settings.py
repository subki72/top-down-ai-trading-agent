import os
from dotenv import load_dotenv

load_dotenv()

# API Keys and Security
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Global Trading Parameters
SYMBOL = 'TAO/USD'

# Timeframe Configuration & Dynamic Candle Limits
TF_MACRO = '1h'    
LIMIT_MACRO = 60 

TF_MICRO = '15m'   
LIMIT_MICRO = 20   

TF_TRIGGER = '5m'  
LIMIT_TRIGGER = 5 

# Technical Thresholds
MIN_RR_RATIO = 1.5
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70