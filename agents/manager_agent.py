from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def synthesize_final_report(state: TradingState):
    """
    Acts as the Chief Investment Officer (CIO).
    Provides the final professional reasoning for the system's decision.
    """
    print("[CEO_AGENT] Compiling executive synthesis...")
    
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    
    template = """
    As the CIO, provide a professional summary for the following analysis:
    - Asset: {asset}
    - Macro Trend: {trend}
    - Setup: {setup}
    - Trigger: {trigger}
    - RR Ratio: 1:{rr}
    - Final Action: {action}

    Requirement: Provide a professional reasoning (max 2 sentences). 
    Focus on confluence and risk mitigation.
    """
    
    prompt = PromptTemplate.from_template(template)
    response = (prompt | llm).invoke({
        "asset": state['asset_pair'],
        "trend": state['macro_trend_h1'],
        "setup": state['micro_signal_m15'],
        "trigger": state['trigger_m5'],
        "rr": state['rr_ratio'],
        "action": state['final_action']
    }).content.strip()

    print(f"[CEO_RESULT] Synthesis complete.")
    return {"execution_logs": [f"CEO Synthesis: {response}"]}