from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def analyze_market_structure_m15(state: TradingState):
    asset = state['asset_pair']
    trend = state['macro_trend_h1']
    raw_data = state['data_m15_raw']
    ind_m15 = state.get('indicators', {}).get('M15', {})
    
    print(f"[M15_AGENT] Searching for {trend} setups...")
    llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
    
    template = """
    Macro Trend Context: {trend}
    Asset: {asset}
    
    Technical Indicators (M15):
    - EMA 13: {ema_13}
    - EMA 21: {ema_21}
    - RSI (14): {rsi}
    - MACD Histogram: {macd}
    
    M15 Data (Last Candles):
    {raw_data}
    
    Task: Identify Chart Patterns (Flags, Triangles, etc.) or SMC (Order Blocks, FVG).
    The pattern MUST align with the Macro Trend ({trend}) and be supported by the M15 momentum indicators.
    
    Format EXACTLY like this: [VALID/INVALID] - [Pattern Name] - [Brief justification, max 10 words]
    """
    
    prompt = PromptTemplate.from_template(template)
    response = (prompt | llm).invoke({
        "asset": asset, 
        "trend": trend, 
        "raw_data": raw_data,
        "ema_13": ind_m15.get("ema_13", "N/A"),
        "ema_21": ind_m15.get("ema_21", "N/A"),
        "rsi": ind_m15.get("rsi", "N/A"),
        "macd": ind_m15.get("macd_hist", "N/A")
    }).content.strip().upper()
    
    is_valid = response.startswith("VALID")
    print(f"[M15_RESULT] Setup Validation: {is_valid} ({response})")
    return {"is_m15_setup_valid": is_valid, "micro_signal_m15": response, "execution_logs": [f"M15 setup analysis: {response}"]}