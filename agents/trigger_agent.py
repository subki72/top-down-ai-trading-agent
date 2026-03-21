from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState

def analyze_entry_trigger_m5(state: TradingState):
    """
    Identifies specific candlestick confirmation on the M5 timeframe.
    Provides exact price levels for Entry, Stop Loss, and Take Profit.
    """
    asset = state['asset_pair']
    context = state['micro_signal_m15']
    raw_data = state['data_m5_raw']
    print(f"[M5_AGENT] Calculating precision trigger for {asset}...")
    
    # Utilizing Llama 3.1 8B for fast, structured output
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    
    template = """
    M15 Setup Context: {context}
    M5 Data (Last 5 Candles):
    {raw_data}
    
    Task: Identify a candlestick trigger (e.g., Engulfing, Marubozu).
    Generate precise price levels for execution.
    
    Strict Format: PATTERN: [Name] | ENTRY: [Price] | SL: [Price] | TP: [Price]
    """
    
    prompt = PromptTemplate.from_template(template)
    response = (prompt | llm).invoke({
        "asset": asset, 
        "context": context, 
        "raw_data": raw_data
    }).content.strip().upper()
    
    print(f"[M5_RESULT] Trigger generated: {response}")
    return {
        "trigger_m5": response, 
        "execution_logs": [f"Entry trigger identified: {response}"]
    }