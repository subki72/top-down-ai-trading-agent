import ccxt
import pandas as pd
from datetime import datetime
from state import TradingState
from config.settings import (
    LIMIT_MACRO,
    LIMIT_MICRO,
    LIMIT_TRIGGER,
    EXCHANGE_ID,
    API_TIMEOUT_SECONDS
)
from tools.indicators import calculate_technical_indicators
from tools.resilience import retry_with_backoff
from config.logger import setup_logger

logger = setup_logger("market_data")

def get_exchange_instance():
    """Initializes CCXT exchange instance with rate limits and timeouts configured."""
    exchange_class = getattr(ccxt, EXCHANGE_ID.lower(), ccxt.kraken)
    exchange = exchange_class({
        'enableRateLimit': True,
        'timeout': API_TIMEOUT_SECONDS * 1000,
    })
    return exchange

def format_sliced_candles(candles: list, limit: int) -> str:
    """Formats last N candles into a compact string representation."""
    if not candles:
        return "NO_DATA_AVAILABLE"
    
    sliced = candles[-limit:] 
    formatted = []
    for candle in sliced:
        ts, open_p, high_p, low_p, close_p, volume = candle[:6]
        timestamp = datetime.fromtimestamp(ts / 1000).strftime('%H:%M')
        formatted.append(f"[{timestamp}] O:{open_p} H:{high_p} L:{low_p} C:{close_p} V:{volume}")
    return "\n".join(formatted)

def fetch_market_data(state: TradingState):
    asset = state.get('asset_pair', 'TAO/USD')
    logger.info(f"Assembling multi-timeframe market data and indicators for {asset} via {EXCHANGE_ID}...")
    exchange = get_exchange_instance()

    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def fetch_timeframe_data(timeframe: str, limit: int = 100):
        return exchange.fetch_ohlcv(asset, timeframe, limit=limit)

    try:
        raw_h1 = fetch_timeframe_data('1h', limit=100)
        raw_m15 = fetch_timeframe_data('15m', limit=100)
        raw_m5 = fetch_timeframe_data('5m', limit=100)
        
        df_h1 = pd.DataFrame(raw_h1, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_m15 = pd.DataFrame(raw_m15, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_m5 = pd.DataFrame(raw_m5, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        ind_h1 = calculate_technical_indicators(df_h1, '1h')
        ind_m15 = calculate_technical_indicators(df_m15, '15m')
        ind_m5 = calculate_technical_indicators(df_m5, '5m')
        
        compiled_indicators = {
            "H1": ind_h1,
            "M15": ind_m15,
            "M5": ind_m5
        }
        
        formatted_h1 = format_sliced_candles(raw_h1, LIMIT_MACRO)
        formatted_m15 = format_sliced_candles(raw_m15, LIMIT_MICRO)
        formatted_m5 = format_sliced_candles(raw_m5, LIMIT_TRIGGER)

        logger.info(f"Market data fetched successfully: H1({len(raw_h1)}), M15({len(raw_m15)}), M5({len(raw_m5)})")
        
        return {
            "data_h1_raw": formatted_h1, 
            "data_m15_raw": formatted_m15, 
            "data_m5_raw": formatted_m5,
            "indicators": compiled_indicators,
            "execution_logs": ["Market data & Indicators successfully synchronized"]
        }
    except Exception as e:
        logger.error(f"Market data fetch failed after retries: {str(e)}", exc_info=True)
        return {
            "data_h1_raw": "", 
            "data_m15_raw": "", 
            "data_m5_raw": "",
            "indicators": {},
            "macro_trend_h1": "SIDEWAYS",
            "final_action": "ERROR_DATA_FETCH",
            "execution_logs": [f"Data synchronization critical error: {str(e)}"]
        }