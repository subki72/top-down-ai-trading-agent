import os
from langgraph.graph import StateGraph, START, END
from state import TradingState

# Importing specialized modular components
from tools.market_data import fetch_market_data
from tools.telegram_notifier import send_telegram_report
from agents.trend_agent import analyze_market_trend_h1
from agents.pattern_agent import analyze_market_structure_m15
from agents.trigger_agent import analyze_entry_trigger_m5
from guardrails.risk_manager import validate_risk_reward
from agents.manager_agent import synthesize_final_report

# ==========================================
# 1. ROUTING LOGIC (The Switchboard)
# ==========================================
def route_macro_to_micro(state: TradingState):
    """
    Routes the workflow based on the macro trend identification.
    """
    if state["macro_trend_h1"] in ["BULLISH", "BEARISH"]:
        return "proceed_to_m15"
    return "abort_to_telegram"

def route_setup_to_trigger(state: TradingState):
    """
    Routes the workflow based on the M15 setup validation.
    """
    if state["is_m15_setup_valid"]:
        return "proceed_to_m5"
    return "abort_to_telegram"

# ==========================================
# 2. GRAPH ASSEMBLY
# ==========================================
workflow = StateGraph(TradingState)

# Node Registration
workflow.add_node("Data_Fetcher", fetch_market_data)
workflow.add_node("H1_Strategist", analyze_market_trend_h1)
workflow.add_node("M15_Analyst", analyze_market_structure_m15)
workflow.add_node("M5_Sniper", analyze_entry_trigger_m5)
workflow.add_node("Risk_Guard", validate_risk_reward)
workflow.add_node("CIO_Manager", synthesize_final_report)
workflow.add_node("Telegram_Dispatcher", send_telegram_report)

# Defining Data Flow (Edges)
workflow.add_edge(START, "Data_Fetcher")
workflow.add_edge("Data_Fetcher", "H1_Strategist")

# Conditional Pathways
workflow.add_conditional_edges("H1_Strategist", route_macro_to_micro, {
    "proceed_to_m15": "M15_Analyst", 
    "abort_to_telegram": "Telegram_Dispatcher" 
})

workflow.add_conditional_edges("M15_Analyst", route_setup_to_trigger, {
    "proceed_to_m5": "M5_Sniper", 
    "abort_to_telegram": "Telegram_Dispatcher"
})

# Final Sequential Execution
workflow.add_edge("M5_Sniper", "Risk_Guard")
workflow.add_edge("Risk_Guard", "CIO_Manager")
workflow.add_edge("CIO_Manager", "Telegram_Dispatcher")
workflow.add_edge("Telegram_Dispatcher", END)

# Final Compilation of the Trading Firm engine
trading_firm = workflow.compile()