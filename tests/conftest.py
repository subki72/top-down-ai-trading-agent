import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_ohlcv_dataframe():
    """Generates a realistic 60-candle DataFrame for testing indicators."""
    np.random.seed(42)
    n_candles = 60
    base_price = 100.0
    
    # Generate random walk price series
    returns = np.random.normal(0.001, 0.015, n_candles)
    close_prices = base_price * np.cumprod(1 + returns)
    
    high_prices = close_prices * (1 + np.abs(np.random.normal(0.005, 0.005, n_candles)))
    low_prices = close_prices * (1 - np.abs(np.random.normal(0.005, 0.005, n_candles)))
    open_prices = (close_prices + np.roll(close_prices, 1)) / 2
    open_prices[0] = base_price
    volumes = np.random.uniform(500, 5000, n_candles)
    timestamps = [1700000000000 + i * 3600000 for i in range(n_candles)]
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    return df

@pytest.fixture
def bullish_valid_state():
    return {
        "asset_pair": "TAO/USD",
        "macro_trend_h1": "BULLISH",
        "is_m15_setup_valid": True,
        "micro_signal_m15": "VALID - Bull Flag - EMA 21 Bounce",
        "trigger_m5": "ANALYSIS: Strong bullish engulfing candle\nPATTERN: Bullish Engulfing | ENTRY: 300.0 | SL: 290.0 | TP: 320.0",
        "is_risk_reward_valid": False,
        "rr_ratio": 0.0,
        "final_action": "IDLE",
        "execution_logs": []
    }

@pytest.fixture
def bearish_valid_state():
    return {
        "asset_pair": "TAO/USD",
        "macro_trend_h1": "BEARISH",
        "is_m15_setup_valid": True,
        "micro_signal_m15": "VALID - Bear Flag - Resistance rejection",
        "trigger_m5": "ANALYSIS: Bearish pinbar rejection at resistance\nPATTERN: Pinbar | ENTRY: 300.0 | SL: 310.0 | TP: 280.0",
        "is_risk_reward_valid": False,
        "rr_ratio": 0.0,
        "final_action": "IDLE",
        "execution_logs": []
    }
