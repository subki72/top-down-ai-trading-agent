import ta
import pandas as pd

def calculate_technical_indicators(df: pd.DataFrame):
    """
    Calculates RSI and MACD Histogram using the 'ta' library.
    Returns a dictionary of the most recent values.
    """
    print("[INDICATORS] Processing technical analysis...")
    
    try:
        # RSI Calculation
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        
        # MACD Calculation
        macd_calc = ta.trend.MACD(close=df['close'])
        df['MACD_HIST'] = macd_calc.macd_diff() 

        latest = df.iloc[-1]
        
        results = {
            "rsi": round(float(latest['RSI']), 2),
            "macd_hist": round(float(latest['MACD_HIST']), 4),
            "last_close": float(latest['close'])
        }
        
        print(f"[INDICATORS] Metrics: RSI {results['rsi']} | MACD Hist {results['macd_hist']}")
        return results

    except Exception as e:
        print(f"[ERROR] Indicator calculation failed: {str(e)}")
        return None