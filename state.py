import operator
from typing import TypedDict, Annotated

class TradingState(TypedDict):
    """
    Centralized state for the LangGraph workflow.
    Ensures data consistency across all specialized agents.
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
    is_risk_reward_valid: bool   
    rr_ratio: float              
    final_action: str
    execution_logs: Annotated[list[str], operator.add]