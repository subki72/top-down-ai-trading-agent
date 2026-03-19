# tools/market_data.py
import ccxt
import pandas as pd
from config.settings import TF_MACRO, TF_MICRO, TF_TRIGGER

def get_multi_timeframe_data(symbol='BTC/USDT', limit=100):
    """
    Fetches data across 3 timeframes simultaneously: Macro (1h), Micro (15m), and Trigger (5m).
    """
    print(f"[TOOLS - MARKET DATA] Initializing Top-Down data retrieval for {symbol}...")
    
    try:
        exchange = ccxt.kraken()
        market_data = {}
        
        # Define timeframe mapping
        timeframe_mapping = {
            'macro': TF_MACRO,
            'micro': TF_MICRO,
            'trigger': TF_TRIGGER
        }
        
        # Sequentially fetch data for each timeframe
        for tf_name, tf_value in timeframe_mapping.items():
            print(f"  -> Fetching {tf_name} data ({tf_value})...")
            bars = exchange.fetch_ohlcv(symbol, timeframe=tf_value, limit=limit)
            
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            market_data[tf_name] = df
            
        print("[TOOLS - MARKET DATA] All timeframe data successfully retrieved.")
        return market_data
        
    except Exception as e:
        print(f"[TOOLS - MARKET DATA ERROR] Failed to connect to exchange: {e}")
        return None