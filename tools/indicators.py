# tools/indicators.py
import ta

def calculate_indicators(df):
    """
    Receives a raw price DataFrame, calculates technical indicators,
    and returns the values ONLY for the latest candlestick.
    """
    print("[TOOLS - INDICATORS] Calculating RSI, MACD, and Moving Average Volume...")
    
    try:
        # Calculate indicators for the entire DataFrame
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        macd = ta.trend.MACD(close=df['close'])
        df['MACD_Histogram'] = macd.macd_diff() 
        df['Volume_MA20'] = df['volume'].rolling(window=20).mean()

        # Extract the latest row (real-time data)
        latest_data = df.iloc[-1]

        # Return results as a structured dictionary
        indicator_results = {
            "rsi": latest_data['RSI'],
            "macd_hist": latest_data['MACD_Histogram'],
            "current_volume": latest_data['volume'],
            "avg_volume": latest_data['Volume_MA20']
        }
        
        print("[TOOLS - INDICATORS] Calculations completed successfully.")
        return indicator_results

    except Exception as e:
        print(f"[TOOLS - INDICATORS ERROR] Failed to calculate indicators: {e}")
        return None