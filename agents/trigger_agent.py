from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def analyze_entry_trigger_m5(state: TradingState):
    asset = state['asset_pair']
    context = state['micro_signal_m15']
    raw_data = state['data_m5_raw']
    ind_m5 = state.get('indicators', {}).get('M5', {})
    
    print(f"[M5_AGENT] Calculating precision trigger for {asset}...")
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")

    template = """
    M15 Setup Context: {context}
    
    Momentum Indicators (M5):
    - RSI (14): {rsi} (Warning: >70 is Overbought, <30 is Oversold)
    - MACD Histogram: {macd}
    - Last Close Price: {last_close}
    
    M5 Data (Last 5 Candles):
    {raw_data}
    
    Task: Identify a candlestick trigger (e.g., Engulfing, Piercing Line).
    1. Explain your reasoning analytically based on the pattern and momentum.
    2. Generate precise price levels for execution.
    
    FORMAT REQUIREMENT: Do not use markdown symbols like asterisks (*) or hashes (#). Use plain text.
    Structure your response exactly like this:
    ANALYSIS: [Your detailed reasoning here]
    PATTERN: [Name] | ENTRY: [Price] | SL: [Price] | TP: [Price]
    """
    
    prompt = PromptTemplate.from_template(template)
    raw_response = (prompt | llm).invoke({
        "asset": asset, 
        "context": context, 
        "raw_data": raw_data,
        "rsi": ind_m5.get("rsi", "N/A"),
        "macd": ind_m5.get("macd_hist", "N/A"),
        "last_close": ind_m5.get("last_close", "N/A")
    }).content.strip().upper()
    
    clean_response = raw_response.replace("*", "").replace("#", "")
    print(f"\n[M5_RESULT] Trigger generated:\n{'-'*40}\n{clean_response}\n{'-'*40}\n")
    
    return {
        "trigger_m5": clean_response, 
        "execution_logs": [f"Entry trigger identified:\n{clean_response}"]
    }