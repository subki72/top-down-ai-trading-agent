import math
import ta
import pandas as pd
from typing import Dict, Any
from config.logger import setup_logger

logger = setup_logger("indicators")

def _safe_float(val: Any, decimals: int = 2, fallback: float = 0.0) -> float:
    """Safely converts a value to float, handles NaN/exceptions, and rounds."""
    try:
        f_val = float(val)
        return round(f_val, decimals) if not math.isnan(f_val) else fallback
    except (ValueError, TypeError):
        return fallback

safe_float = _safe_float

def calculate_technical_indicators(df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
    """
    Computes technical indicators for a given OHLCV DataFrame.
    Validates minimum length, handles NaN values gracefully, and rounds metrics.
    """
    if df is None or len(df) < 14:
        logger.warning(f"Insufficient data to calculate indicators for {timeframe}. Rows: {len(df) if df is not None else 0}")
        return {}

    try:
        df_copy = df.copy()
        
        # RSI 14
        df_copy['RSI'] = ta.momentum.RSIIndicator(close=df_copy['close'], window=14).rsi()
        
        # MACD (12, 26, 9)
        macd_calc = ta.trend.MACD(close=df_copy['close'])
        df_copy['MACD_HIST'] = macd_calc.macd_diff() 

        # EMAs for macro/micro timeframes
        if timeframe in ['1h', '15m']:
            df_copy['EMA_13'] = ta.trend.EMAIndicator(close=df_copy['close'], window=13).ema_indicator()
            df_copy['EMA_21'] = ta.trend.EMAIndicator(close=df_copy['close'], window=21).ema_indicator()

        latest = df_copy.iloc[-1]

        results = {
            "rsi": _safe_float(latest.get('RSI'), 2, 50.0),
            "macd_hist": _safe_float(latest.get('MACD_HIST'), 4, 0.0),
            "last_close": _safe_float(latest.get('close'), 4, 0.0)
        }

        if timeframe in ['1h', '15m']:
            results["ema_13"] = _safe_float(latest.get('EMA_13'), 2, results["last_close"])
            results["ema_21"] = _safe_float(latest.get('EMA_21'), 2, results["last_close"])
            
        logger.debug(f"Calculated indicators for {timeframe}: {results}")
        return results

    except Exception as e:
        logger.error(f"Indicator calculation failed for {timeframe}: {str(e)}", exc_info=True)
        return {}