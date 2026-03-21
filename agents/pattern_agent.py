from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def analyze_market_structure_m15(state: TradingState):
    """
    Detects Chart Patterns and Smart Money Concepts (SMC) on the M15 timeframe.
    Ensures the setup aligns with the identified macro trend.
    """
    asset = state['asset_pair']
    trend = state['macro_trend_h1']
    raw_data = state['data_m15_raw']
    print(f"[M15_AGENT] Searching for {trend} setups...")
    
    llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
    
    template = """
    Macro Trend Context: {trend}
    Asset: {asset}
    M15 Data (Last 20 Candles):
    {raw_data}
    
    Task: Identify Chart Patterns (Flags, Triangles, etc.) or SMC (Order Blocks, FVG).
    The pattern MUST align with the Macro Trend.
    
    Format: [VALID/INVALID] - [Pattern Name] - [Brief justification, max 10 words]
    """
    
    prompt = PromptTemplate.from_template(template)
    response = (prompt | llm).invoke({
        "asset": asset, 
        "trend": trend, 
        "raw_data": raw_data
    }).content.strip().upper()
    
    is_valid = response.startswith("VALID")
    print(f"[M15_RESULT] Setup Validation: {is_valid} ({response})")
    
    return {
        "is_m15_setup_valid": is_valid, 
        "micro_signal_m15": response, 
        "execution_logs": [f"M15 setup analysis: {response}"]
    }