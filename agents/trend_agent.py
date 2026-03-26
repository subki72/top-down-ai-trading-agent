from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def analyze_market_trend_h1(state: TradingState):
    asset = state['asset_pair']
    raw_data = state['data_h1_raw']
    ind_h1 = state.get('indicators', {}).get('H1', {})
    
    print(f"[H1_AGENT] Analyzing macro structure for {asset}...")
    llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
    
    template = """
    Asset: {asset}
    Timeframe: H1
    
    Technical Indicators (H1):
    - EMA 13: {ema_13}
    - EMA 21: {ema_21}
    - RSI (14): {rsi}
    - MACD Histogram: {macd}
    - Last Close Price: {last_close}
    
    Historical Data (H1 Candles):
    {raw_data}
    
    Task: Determine the Market Structure.
    Rules:
    1. BULLISH: Price is generally above EMA 13 & 21. EMA 13 > EMA 21. Minimum 2 cycles of HH-HL.
    2. BEARISH: Price is generally below EMA 13 & 21. EMA 13 < EMA 21. Minimum 2 cycles of LL-LH.
    3. SIDEWAYS: If price is crossing EMAs frequently or structure is inconsistent.
    
    Response Requirement: Return ONLY one word (BULLISH, BEARISH, or SIDEWAYS).
    """
    
    prompt = PromptTemplate.from_template(template)
    response = (prompt | llm).invoke({
        "asset": asset, 
        "raw_data": raw_data,
        "ema_13": ind_h1.get("ema_13", "N/A"),
        "ema_21": ind_h1.get("ema_21", "N/A"),
        "rsi": ind_h1.get("rsi", "N/A"),
        "macd": ind_h1.get("macd_hist", "N/A"),
        "last_close": ind_h1.get("last_close", "N/A")
    }).content.strip().upper()
    
    print(f"[H1_RESULT] Identified Trend: {response}")
    return {"macro_trend_h1": response, "execution_logs": [f"Macro analysis: {response}"]}