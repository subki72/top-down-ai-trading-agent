import pytest
from tools.market_data import format_sliced_candles, get_exchange_instance

class TestMarketData:
    def test_format_sliced_candles_empty(self):
        assert format_sliced_candles([], 10) == "NO_DATA_AVAILABLE"

    def test_format_sliced_candles_slices_correctly(self):
        candles = [
            [1700000000000, 100, 105, 95, 102, 1000],
            [1700003600000, 102, 108, 101, 107, 1200],
            [1700007200000, 107, 110, 106, 109, 1500],
        ]
        # Request limit 2
        formatted = format_sliced_candles(candles, 2)
        lines = formatted.strip().split("\n")
        assert len(lines) == 2
        assert "O:102" in lines[0]
        assert "O:107" in lines[1]

    def test_get_exchange_instance(self):
        exchange = get_exchange_instance()
        assert exchange is not None
        assert exchange.enableRateLimit is True
        assert exchange.timeout > 0
