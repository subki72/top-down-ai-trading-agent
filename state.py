import operator
from typing import TypedDict, Annotated, Optional

class TradingState(TypedDict, total=False):
    """
    Centralized state for the LangGraph workflow.
    Ensures data consistency across all specialized agents, deterministic guardrails,
    and capital management modules.
    """
    asset_pair: str
    indicators: dict
    data_h1_raw: str             
    data_m15_raw: str            
    data_m5_raw: str             
    macro_trend_h1: str
    is_m15_setup_valid: bool
    micro_signal_m15: str
    trigger_m5: str
    
    # Risk Guardrail & Trade Parameters
    is_risk_reward_valid: bool   
    rr_ratio: float
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    
    # Capital Management & Position Sizing
    position_size_usd: float
    position_size_tokens: float
    risk_usd: float
    reward_usd: float
    risk_rejection_reason: str
    
    # Final Executive Synthesis & Logging
    final_action: str
    execution_logs: Annotated[list[str], operator.add]