from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def analyze_market_trend_h1(state: TradingState):
    """
    Identifies the macro market structure on the H1 timeframe.
    Requires at least two cycles of HH-HL or LL-LH for trend validation.
    """
    asset = state['asset_pair']
    raw_data = state['data_h1_raw']
    print(f"[H1_AGENT] Analyzing macro structure for {asset}...")
    
    # Utilizing Llama 3.3 70B for superior reasoning on market structure
    llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
    
    template = """
    Asset: {asset}
    Timeframe: H1
    Historical Data (24 Candles):
    {raw_data}
    
    Task: Determine the Market Structure.
    Rules:
    - BULLISH: Minimum 2 cycles of Higher Highs (HH) and Higher Lows (HL).
    - BEARISH: Minimum 2 cycles of Lower Lows (LL) and Lower Highs (LH).
    - SIDEWAYS: If structure is inconsistent or ranging.
    
    Response Requirement: Return ONLY one word (BULLISH, BEARISH, or SIDEWAYS).
    """
    
    prompt = PromptTemplate.from_template(template)
    response = (prompt | llm).invoke({"asset": asset, "raw_data": raw_data}).content.strip().upper()
    
    print(f"[H1_RESULT] Identified Trend: {response}")
    return {
        "macro_trend_h1": response, 
        "execution_logs": [f"Macro analysis completed: {response}"]
    }