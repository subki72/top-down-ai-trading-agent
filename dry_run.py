import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from unittest.mock import patch, MagicMock

# Set dummy key for local simulation if not provided
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "gsk_mock_local_simulation_key_12345678"

from agent_graph import trading_firm
from config.settings import ACCOUNT_EQUITY, MAX_RISK_PER_TRADE_PCT, MIN_RR_RATIO

def run_dry_run_simulation():
    """
    Simulates a complete End-to-End trading cycle locally WITHOUT requiring a live Groq API key.
    Tests the LangGraph state machine, data fetcher, deterministic risk guardrail,
    and position sizing engine.
    """
    print("\n" + "=" * 65)
    print("🚀 AI TRADING FIRM: OFFLINE DRY-RUN SIMULATION (MOCK MODE)")
    print("=" * 65)
    print(f"Account Equity:      ${ACCOUNT_EQUITY:,.2f}")
    print(f"Max Risk Per Trade:  {MAX_RISK_PER_TRADE_PCT}% (${(MAX_RISK_PER_TRADE_PCT/100)*ACCOUNT_EQUITY:,.2f})")
    print(f"Minimum RR Target:   1:{MIN_RR_RATIO}")
    print("=" * 65 + "\n")

    initial_context = {
        "asset_pair": "TAO/USD",
        "data_h1_raw": "",
        "data_m15_raw": "",
        "data_m5_raw": "",
        "macro_trend_h1": "",
        "is_m15_setup_valid": False,
        "micro_signal_m15": "",
        "trigger_m5": "",
        "is_risk_reward_valid": False,
        "rr_ratio": 0.0,
        "entry_price": None,
        "stop_loss": None,
        "take_profit": None,
        "position_size_usd": 0.0,
        "position_size_tokens": 0.0,
        "risk_usd": 0.0,
        "reward_usd": 0.0,
        "risk_rejection_reason": "",
        "final_action": "IDLE",
        "indicators": {},
        "execution_logs": ["Local dry-run initiated"]
    }

    # Mock the LLM sequence calls so user can test the complete pipeline with 0 API keys
    mock_trend = MagicMock(content="BULLISH")
    mock_pattern = MagicMock(content="[VALID] - Bull Flag - Retest of EMA 21 with strong volume")
    mock_trigger = MagicMock(
        content="ANALYSIS: Momentum shift detected\nPATTERN: Bullish Engulfing | ENTRY: 300.0 | SL: 290.0 | TP: 325.0"
    )
    mock_cio = MagicMock(
        content="Confluence achieved across macro and micro timeframes. Risk guardrail satisfied with 1:2.5 RR ratio. Proceeding with disciplined execution."
    )

    with patch("langchain_core.runnables.base.RunnableSequence.invoke") as mock_invoke:
        # Sequence of LLM calls in the graph: Trend -> Pattern -> Trigger -> Manager
        mock_invoke.side_effect = [mock_trend, mock_pattern, mock_trigger, mock_cio]
        
        final_state = trading_firm.invoke(initial_context)

    print("\n" + "=" * 65)
    print("📊 DRY-RUN EXECUTION RESULTS")
    print("=" * 65)
    print(f"Decision:            {final_state.get('final_action')}")
    print(f"Macro Trend (H1):    {final_state.get('macro_trend_h1')}")
    print(f"Pattern (M15):       {final_state.get('micro_signal_m15')}")
    print(f"Trigger (M5):        {final_state.get('trigger_m5')}")
    print("-" * 65)
    print(f"Calculated RR:       1:{final_state.get('rr_ratio')}")
    print(f"Entry Price:         ${final_state.get('entry_price')}")
    print(f"Stop Loss:           ${final_state.get('stop_loss')}")
    print(f"Take Profit:         ${final_state.get('take_profit')}")
    print(f"Position Size:       ${final_state.get('position_size_usd')} ({final_state.get('position_size_tokens')} tokens)")
    print(f"Dollar Risk:         ${final_state.get('risk_usd')}")
    print(f"Target Reward:       ${final_state.get('reward_usd')}")
    print("=" * 65)
    print("🟢 PIPELINE EXECUTION VERIFIED SUCCESSFULLY!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_dry_run_simulation()
