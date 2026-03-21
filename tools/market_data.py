import ccxt
import pandas as pd
from datetime import datetime
from state import TradingState

def fetch_market_data(state: TradingState):
    """
    Fetches multi-timeframe OHLCV data from Kraken.
    Prepares raw strings for LLM analysis.
    """
    asset = state['asset_pair']
    print(f"[DATA_FETCHER] Fetching data for {asset}...")
    exchange = ccxt.kraken()
    
    try:
        # Fetching raw data
        ohlcv_h1 = exchange.fetch_ohlcv(asset, '1h', limit=24)
        ohlcv_m15 = exchange.fetch_ohlcv(asset, '15m', limit=20)
        ohlcv_m5 = exchange.fetch_ohlcv(asset, '5m', limit=5)
        
        def format_candles(candles):
            formatted = ""
            for c in candles:
                timestamp = datetime.fromtimestamp(c[0]/1000).strftime('%H:%M')
                formatted += f"[{timestamp}] O:{c[1]} H:{c[2]} L:{c[3]} C:{c[4]} V:{c[5]}\n"
            return formatted
            
        return {
            "data_h1_raw": format_candles(ohlcv_h1), 
            "data_m15_raw": format_candles(ohlcv_m15), 
            "data_m5_raw": format_candles(ohlcv_m5),
            "execution_logs": ["Successfully retrieved multi-timeframe market data"]
        }
    except Exception as e:
        print(f"[ERROR] Market data acquisition failed: {str(e)}")
        return {"execution_logs": [f"Market data error: {str(e)}"]}