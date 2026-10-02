from langgraph.graph import StateGraph, START, END
from state import TradingState
from config.logger import setup_logger

# Specialized modular components
from tools.market_data import fetch_market_data
from tools.telegram_notifier import send_telegram_report
from tools.web_notifier import send_web_report
from agents.trend_agent import analyze_market_trend_h1
from agents.pattern_agent import analyze_market_structure_m15
from agents.trigger_agent import analyze_entry_trigger_m5
from guardrails.risk_manager import validate_risk_reward
from agents.manager_agent import synthesize_final_report

logger = setup_logger("agent_graph")

# ==========================================
# 1. ROUTING LOGIC (The Switchboard)
# ==========================================
def route_macro_to_micro(state: TradingState) -> str:
    """
    Routes the workflow based on the macro trend identification.
    Short-circuits if macro trend is unclear or sideways to conserve compute.
    """
    trend = state.get("macro_trend_h1", "SIDEWAYS")
    if trend in ["BULLISH", "BEARISH"]:
        logger.info(f"Routing to M15 Analyst: Macro trend confirmed as {trend}")
        return "proceed_to_m15"
    logger.info(f"Short-circuiting workflow: Macro trend is {trend}. Aborting to dispatcher.")
    return "abort_to_dispatch"

def route_setup_to_trigger(state: TradingState) -> str:
    """
    Routes the workflow based on the M15 setup validation.
    Short-circuits if no valid chart or SMC pattern was detected.
    """
    if state.get("is_m15_setup_valid", False):
        logger.info("Routing to M5 Sniper: M15 setup pattern validated")
        return "proceed_to_m5"
    logger.info("Short-circuiting workflow: M15 setup invalid. Aborting to dispatcher.")
    return "abort_to_dispatch"

# ==========================================
# 2. DISPATCH HUB (Telegram + Web parallel)
# ==========================================
def dispatch_all_reports(state: TradingState):
    """
    Central dispatch node that dispatches reports to both 
    Telegram bot and Web Dashboard asynchronously.
    """
    logger.info("Executing central report dispatch...")
    
    # Ensure final_action has an informative value if short-circuited
    current_action = state.get("final_action", "IDLE")
    if current_action == "IDLE":
        if state.get("macro_trend_h1") not in ["BULLISH", "BEARISH"]:
            state["final_action"] = "STANDBY_SIDEWAYS_MARKET"
        elif not state.get("is_m15_setup_valid", False):
            state["final_action"] = "STANDBY_NO_VALID_SETUP"

    telegram_result = send_telegram_report(state)
    web_result = send_web_report(state)
    
    logs = []
    logs.extend(telegram_result.get("execution_logs", []))
    logs.extend(web_result.get("execution_logs", []))
    
    return {"execution_logs": logs, "final_action": state.get("final_action", current_action)}

# ==========================================
# 3. GRAPH ASSEMBLY
# ==========================================
workflow = StateGraph(TradingState)

# Node Registration
workflow.add_node("Data_Fetcher", fetch_market_data)
workflow.add_node("H1_Strategist", analyze_market_trend_h1)
workflow.add_node("M15_Analyst", analyze_market_structure_m15)
workflow.add_node("M5_Sniper", analyze_entry_trigger_m5)
workflow.add_node("Risk_Guard", validate_risk_reward)
workflow.add_node("CIO_Manager", synthesize_final_report)
workflow.add_node("Report_Dispatcher", dispatch_all_reports)

# Defining Data Flow (Edges)
workflow.add_edge(START, "Data_Fetcher")
workflow.add_edge("Data_Fetcher", "H1_Strategist")

# Conditional Pathways
workflow.add_conditional_edges("H1_Strategist", route_macro_to_micro, {
    "proceed_to_m15": "M15_Analyst", 
    "abort_to_dispatch": "Report_Dispatcher" 
})

workflow.add_conditional_edges("M15_Analyst", route_setup_to_trigger, {
    "proceed_to_m5": "M5_Sniper", 
    "abort_to_dispatch": "Report_Dispatcher"
})

# Sequential Execution for Valid Setups
workflow.add_edge("M5_Sniper", "Risk_Guard")
workflow.add_edge("Risk_Guard", "CIO_Manager")
workflow.add_edge("CIO_Manager", "Report_Dispatcher")
workflow.add_edge("Report_Dispatcher", END)

# Final Compilation of the Trading Firm engine
trading_firm = workflow.compile()