import ta
import pandas as pd

def calculate_technical_indicators(df: pd.DataFrame, timeframe: str):
    """
    Kalkulator Indikator Spesifik.
    Semua kalkulasi diselesaikan DULU sebelum baris terakhir diambil.
    """
    try:
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        macd_calc = ta.trend.MACD(close=df['close'])
        df['MACD_HIST'] = macd_calc.macd_diff() 

        if timeframe in ['1h', '15m']:
            df['EMA_13'] = ta.trend.EMAIndicator(close=df['close'], window=13).ema_indicator()
            df['EMA_21'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()
        latest = df.iloc[-1]
        
        results = {
            "rsi": round(float(latest['RSI']), 2),
            "macd_hist": round(float(latest['MACD_HIST']), 4),
            "last_close": float(latest['close'])
        }

        if timeframe in ['1h', '15m']:
            results["ema_13"] = round(float(latest['EMA_13']), 2)
            results["ema_21"] = round(float(latest['EMA_21']), 2)
            
        return results

    except Exception as e:
        print(f"[ERROR] Indicator calculation failed for {timeframe}: {str(e)}")
        return {}