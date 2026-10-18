"""Unified high-level facade for Top-Down AI Trading Agent architecture."""

from typing import Any, Dict
from agent_graph import run_trading_pipeline
from state import AgentState


def analyze_market_symbol(symbol: str = "BTC-USD") -> Dict[str, Any]:
    """Execute complete top-down multi-agent market analysis."""
    return run_trading_pipeline(symbol=symbol)
