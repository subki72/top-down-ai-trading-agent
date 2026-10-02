import pytest
from guardrails.risk_manager import (
    safe_extract_price,
    calculate_position_sizing,
    validate_directional_levels,
    validate_risk_reward,
)

class TestSafeExtractPrice:
    def test_standard_format(self):
        text = "PATTERN: Engulfing | ENTRY: 350.50 | SL: 340.00 | TP: 375.00"
        assert safe_extract_price("ENTRY", text) == 350.50
        assert safe_extract_price("SL", text) == 340.00
        assert safe_extract_price("TP", text) == 375.00

    def test_dollar_sign_and_spaces(self):
        text = "Entry Price = $1,250.75 and SL: $1,200.00 with TP - $1,350.00"
        assert safe_extract_price("ENTRY", text) == 1250.75
        assert safe_extract_price("SL", text) == 1200.00
        assert safe_extract_price("TP", text) == 1350.00

    def test_missing_price_returns_none(self):
        text = "ENTRY: 350.0 | TP: 370.0"
        assert safe_extract_price("SL", text) is None
        assert safe_extract_price("UNKNOWN", text) is None
        assert safe_extract_price("ENTRY", "") is None


class TestDirectionalValidation:
    def test_bullish_valid(self):
        # Long: SL < Entry < TP
        is_valid, msg = validate_directional_levels("BULLISH", entry=100.0, sl=95.0, tp=110.0)
        assert is_valid is True

    def test_bullish_invalid_sl_above_entry(self):
        is_valid, msg = validate_directional_levels("BULLISH", entry=100.0, sl=105.0, tp=115.0)
        assert is_valid is False
        assert "SL" in msg

    def test_bullish_invalid_tp_below_entry(self):
        is_valid, msg = validate_directional_levels("BULLISH", entry=100.0, sl=90.0, tp=95.0)
        assert is_valid is False
        assert "TP" in msg

    def test_bearish_valid(self):
        # Short: TP < Entry < SL
        is_valid, msg = validate_directional_levels("BEARISH", entry=100.0, sl=105.0, tp=90.0)
        assert is_valid is True

    def test_bearish_invalid_sl_below_entry(self):
        is_valid, msg = validate_directional_levels("BEARISH", entry=100.0, sl=95.0, tp=85.0)
        assert is_valid is False
        assert "SL" in msg

    def test_bearish_invalid_tp_above_entry(self):
        is_valid, msg = validate_directional_levels("BEARISH", entry=100.0, sl=110.0, tp=105.0)
        assert is_valid is False
        assert "TP" in msg


class TestPositionSizing:
    def test_basic_position_sizing(self):
        # $10,000 equity, 1% risk = $100 risk
        # Entry 100, SL 95 -> risk per unit = 5
        # Units = 100 / 5 = 20 tokens
        # Position USD = 20 * 100 = $2,000
        res = calculate_position_sizing(
            entry=100.0,
            sl=95.0,
            tp=115.0,
            equity=10000.0,
            max_risk_pct=1.0,
            max_alloc_pct=25.0
        )
        assert res["position_size_tokens"] == 20.0
        assert res["position_size_usd"] == 2000.0
        assert res["risk_usd"] == 100.0
        assert res["reward_usd"] == 300.0

    def test_position_capped_by_max_allocation(self):
        # If stop loss is very tight: entry 100, sl 99.5 (risk = 0.5)
        # $100 risk / 0.5 = 200 tokens -> $20,000 USD (which exceeds 25% = $2,500 limit)
        # It should cap at $2,500 USD = 25 tokens
        res = calculate_position_sizing(
            entry=100.0,
            sl=99.5,
            tp=102.0,
            equity=10000.0,
            max_risk_pct=1.0,
            max_alloc_pct=25.0
        )
        assert res["position_size_usd"] == 2500.0
        assert res["position_size_tokens"] == 25.0
        assert res["risk_usd"] == 12.5


class TestValidateRiskReward:
    def test_valid_trade_execution(self, bullish_valid_state):
        # Entry 300, SL 290, TP 320 -> Risk=10, Reward=20 -> RR = 2.0 (>= 1.5)
        result = validate_risk_reward(bullish_valid_state)
        assert result["is_risk_reward_valid"] is True
        assert result["rr_ratio"] == 2.0
        assert result["final_action"] == "EXECUTE_TRADE"
        assert result["position_size_usd"] > 0

    def test_poor_rr_rejected(self, bullish_valid_state):
        # Entry 300, SL 290, TP 310 -> Risk=10, Reward=10 -> RR = 1.0 (< 1.5)
        bullish_valid_state["trigger_m5"] = "PATTERN: Engulfing | ENTRY: 300.0 | SL: 290.0 | TP: 310.0"
        result = validate_risk_reward(bullish_valid_state)
        assert result["is_risk_reward_valid"] is False
        assert result["rr_ratio"] == 1.0
        assert result["final_action"] == "REJECT_BAD_RR"

    def test_inverted_geometry_rejected(self, bullish_valid_state):
        # Bullish but SL is above Entry
        bullish_valid_state["trigger_m5"] = "PATTERN: Engulfing | ENTRY: 300.0 | SL: 310.0 | TP: 330.0"
        result = validate_risk_reward(bullish_valid_state)
        assert result["is_risk_reward_valid"] is False
        assert result["final_action"] == "REJECT_INVALID_GEOMETRY"

    def test_missing_price_rejected(self, bullish_valid_state):
        bullish_valid_state["trigger_m5"] = "I cannot determine price levels for this asset."
        result = validate_risk_reward(bullish_valid_state)
        assert result["is_risk_reward_valid"] is False
        assert result["final_action"] == "REJECT_INVALID_FORMAT"
