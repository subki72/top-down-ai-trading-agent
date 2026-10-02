import pytest
from agents.trend_agent import parse_trend_output
from agents.pattern_agent import parse_pattern_output
from agents.news_classifier_agent import safe_parse_json_array

class TestTrendParser:
    def test_clean_single_word(self):
        assert parse_trend_output("BULLISH") == "BULLISH"
        assert parse_trend_output("BEARISH") == "BEARISH"
        assert parse_trend_output("SIDEWAYS") == "SIDEWAYS"

    def test_lowercase_and_whitespace(self):
        assert parse_trend_output("  bullish \n") == "BULLISH"

    def test_markdown_and_conversational_text(self):
        assert parse_trend_output("**BULLISH**") == "BULLISH"
        assert parse_trend_output("Based on technical structure, the market is BEARISH.") == "BEARISH"

    def test_unrecognized_defaults_to_sideways(self):
        assert parse_trend_output("I am not sure about this market.") == "SIDEWAYS"
        assert parse_trend_output("") == "SIDEWAYS"
        assert parse_trend_output(None) == "SIDEWAYS"


class TestPatternParser:
    def test_clean_valid_format(self):
        is_valid, signal = parse_pattern_output("VALID - Bull Flag - Retest of EMA 21")
        assert is_valid is True
        assert "VALID" in signal

    def test_bracketed_valid(self):
        is_valid, signal = parse_pattern_output("[VALID] - Order Block - Clean FVG")
        assert is_valid is True

    def test_clean_invalid_format(self):
        is_valid, signal = parse_pattern_output("INVALID - Choppy price action")
        assert is_valid is False

    def test_markdown_bold_valid(self):
        is_valid, signal = parse_pattern_output("**VALID** - Double Bottom")
        assert is_valid is True

    def test_empty_or_none(self):
        is_valid, signal = parse_pattern_output("")
        assert is_valid is False


class TestNewsJsonParser:
    def test_standard_json_array(self):
        raw = '[{"index": 0, "category": "FUNDAMENTAL_MACRO", "sentiment": "BEARISH", "summary": "Fed cuts rates"}]'
        parsed = safe_parse_json_array(raw)
        assert len(parsed) == 1
        assert parsed[0]["category"] == "FUNDAMENTAL_MACRO"
        assert parsed[0]["sentiment"] == "BEARISH"

    def test_markdown_code_block(self):
        raw = """```json
[
  {"index": 0, "category": "TECHNICAL", "sentiment": "BULLISH", "summary": "BTC breaks 100k"}
]
```"""
        parsed = safe_parse_json_array(raw)
        assert len(parsed) == 1
        assert parsed[0]["category"] == "TECHNICAL"

    def test_corrupted_json_returns_empty_list(self):
        raw = "Here is the result: [invalid json content"
        assert safe_parse_json_array(raw) == []
