import pytest
import pandas as pd
import numpy as np
from tools.backtester import StrategyBacktester

class TestBacktester:
    def test_backtester_with_synthetic_trend(self, sample_ohlcv_dataframe):
        # Add indicator columns to sample dataframe
        df = sample_ohlcv_dataframe.copy()
        df['ema_13'] = df['close'].ewm(span=13, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['rsi'] = 50.0  # Constant neutral RSI

        backtester = StrategyBacktester(
            initial_equity=10000.0,
            risk_per_trade_pct=1.0,
            min_rr_ratio=1.5
        )
        results = backtester.run_backtest(df)

        assert "initial_equity" in results
        assert "final_equity" in results
        assert "total_return_pct" in results
        assert "win_rate_pct" in results
        assert "max_drawdown_pct" in results
        assert results["initial_equity"] == 10000.0

    def test_backtester_insufficient_data(self, sample_ohlcv_dataframe):
        short_df = sample_ohlcv_dataframe.iloc[:10]
        backtester = StrategyBacktester()
        results = backtester.run_backtest(short_df)
        assert "error" in results
