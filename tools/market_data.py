import ccxt
import pandas as pd
from datetime import datetime
from state import TradingState
from config.settings import LIMIT_MACRO, LIMIT_MICRO, LIMIT_TRIGGER
from tools.indicators import calculate_technical_indicators 

def fetch_market_data(state: TradingState):
    asset = state['asset_pair']
    print(f"[DATA_FETCHER] Assembling Data & Indicators for {asset}...")
    exchange = ccxt.kraken()
    
    try:
        raw_h1 = exchange.fetch_ohlcv(asset, '1h', limit=100)
        raw_m15 = exchange.fetch_ohlcv(asset, '15m', limit=100)
        raw_m5 = exchange.fetch_ohlcv(asset, '5m', limit=100)
        
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
        
        def format_sliced_candles(candles, limit):
            sliced = candles[-limit:] 
            formatted = ""
            for c in sliced:
                timestamp = datetime.fromtimestamp(c[0]/1000).strftime('%H:%M')
                formatted += f"[{timestamp}] O:{c[1]} H:{c[2]} L:{c[3]} C:{c[4]} V:{c[5]}\n"
            return formatted
            
        return {
            "data_h1_raw": format_sliced_candles(raw_h1, LIMIT_MACRO), 
            "data_m15_raw": format_sliced_candles(raw_m15, LIMIT_MICRO), 
            "data_m5_raw": format_sliced_candles(raw_m5, LIMIT_TRIGGER),
            "indicators": compiled_indicators,
            "execution_logs": ["Market data & Indicators successfully synchronized"]
        }
    except Exception as e:
        print(f"[ERROR] Data Fetcher failed: {str(e)}")
        return {"execution_logs": [f"Data synchronization error: {str(e)}"]}