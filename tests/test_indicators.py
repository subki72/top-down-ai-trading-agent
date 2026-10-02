import pytest
import pandas as pd
from tools.indicators import calculate_technical_indicators

class TestTechnicalIndicators:
    def test_indicators_with_valid_data(self, sample_ohlcv_dataframe):
        indicators = calculate_technical_indicators(sample_ohlcv_dataframe, '1h')
        
        assert "rsi" in indicators
        assert "macd_hist" in indicators
        assert "last_close" in indicators
        assert "ema_13" in indicators
        assert "ema_21" in indicators

        # Value bounds checks
        assert 0.0 <= indicators["rsi"] <= 100.0
        assert isinstance(indicators["macd_hist"], float)
        assert indicators["last_close"] > 0

    def test_indicators_m5_timeframe_omits_long_emas(self, sample_ohlcv_dataframe):
        indicators = calculate_technical_indicators(sample_ohlcv_dataframe, '5m')
        
        assert "rsi" in indicators
        assert "macd_hist" in indicators
        assert "last_close" in indicators
        # EMAs are only computed for 1h and 15m
        assert "ema_13" not in indicators

    def test_empty_dataframe_returns_empty_dict(self):
        empty_df = pd.DataFrame()
        result = calculate_technical_indicators(empty_df, '1h')
        assert result == {}

    def test_short_dataframe_returns_empty_dict(self, sample_ohlcv_dataframe):
        short_df = sample_ohlcv_dataframe.iloc[:5]
        result = calculate_technical_indicators(short_df, '1h')
        assert result == {}
