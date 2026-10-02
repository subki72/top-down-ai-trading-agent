import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState
from config.settings import MODEL_SNIPER, API_TIMEOUT_SECONDS
from config.logger import setup_logger
from tools.resilience import retry_with_backoff

logger = setup_logger("trigger_agent")

def analyze_entry_trigger_m5(state: TradingState):
    asset = state.get('asset_pair', 'UNKNOWN')
    context = state.get('micro_signal_m15', '')
    raw_data = state.get('data_m5_raw', '')
    ind_m5 = state.get('indicators', {}).get('M5', {})
    
    logger.info(f"Calculating precision trigger for {asset} on M5 timeframe...")

    template = """
    M15 Setup Context: {context}
    
    Momentum Indicators (M5):
    - RSI (14): {rsi} (Warning: >70 is Overbought, <30 is Oversold)
    - MACD Histogram: {macd}
    - Last Close Price: {last_close}
    
    M5 Data (Last 5 Candles):
    {raw_data}
    
    Task: Identify a candlestick trigger (e.g., Engulfing, Piercing Line, Pinbar).
    1. Explain your reasoning analytically based on the pattern and momentum.
    2. Generate precise price levels for execution.
    
    FORMAT REQUIREMENT: Do not use markdown symbols like asterisks (*) or hashes (#). Use plain text.
    Structure your response exactly like this:
    ANALYSIS: [Your detailed reasoning here]
    PATTERN: [Name] | ENTRY: [Price] | SL: [Price] | TP: [Price]
    """

    prompt = PromptTemplate.from_template(template)
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def call_llm():
        llm = ChatGroq(
            temperature=0,
            model_name=MODEL_SNIPER,
            request_timeout=API_TIMEOUT_SECONDS
        )
        return (prompt | llm).invoke({
            "asset": asset, 
            "context": context, 
            "raw_data": raw_data,
            "rsi": ind_m5.get("rsi", "N/A"),
            "macd": ind_m5.get("macd_hist", "N/A"),
            "last_close": ind_m5.get("last_close", "N/A")
        }).content

    try:
        raw_response = call_llm()
        clean_response = raw_response.replace("*", "").replace("#", "").strip()
        logger.info(f"M5 Trigger Generated successfully. Snippet: {clean_response[:100]}...")
        return {
            "trigger_m5": clean_response, 
            "execution_logs": [f"Entry trigger identified:\n{clean_response}"]
        }
    except Exception as e:
        logger.error(f"M5 Trigger Agent failed: {str(e)}", exc_info=True)
        fallback_msg = f"TRIGGER_FAILURE: Error generating trigger - {str(e)}"
        return {
            "trigger_m5": fallback_msg,
            "execution_logs": [f"M5 trigger agent error: {str(e)}"]
        }