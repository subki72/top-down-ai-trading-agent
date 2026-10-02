import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState
from config.settings import MODEL_STRATEGIST, API_TIMEOUT_SECONDS
from config.logger import setup_logger
from tools.resilience import retry_with_backoff

logger = setup_logger("trend_agent")

def parse_trend_output(raw_text: str) -> str:
    """
    Robustly extracts trend direction (BULLISH, BEARISH, or SIDEWAYS)
    from LLM responses, even if there is surrounding conversational text or markdown.
    """
    if not raw_text:
        return "SIDEWAYS"
    
    cleaned = raw_text.strip().upper()
    
    # Direct match
    if cleaned in ["BULLISH", "BEARISH", "SIDEWAYS"]:
        return cleaned
    
    # Regex search for explicit keywords
    match = re.search(r'\b(BULLISH|BEARISH|SIDEWAYS)\b', cleaned)
    if match:
        return match.group(1)
        
    logger.warning(f"Unrecognized trend output format: '{raw_text}'. Defaulting to SIDEWAYS.")
    return "SIDEWAYS"

def analyze_market_trend_h1(state: TradingState):
    asset = state.get('asset_pair', 'UNKNOWN')
    raw_data = state.get('data_h1_raw', '')
    ind_h1 = state.get('indicators', {}).get('H1', {})
    
    logger.info(f"Analyzing macro structure for {asset} using model {MODEL_STRATEGIST}...")

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
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def call_llm():
        llm = ChatGroq(
            temperature=0,
            model_name=MODEL_STRATEGIST,
            request_timeout=API_TIMEOUT_SECONDS
        )
        return (prompt | llm).invoke({
            "asset": asset, 
            "raw_data": raw_data,
            "ema_13": ind_h1.get("ema_13", "N/A"),
            "ema_21": ind_h1.get("ema_21", "N/A"),
            "rsi": ind_h1.get("rsi", "N/A"),
            "macd": ind_h1.get("macd_hist", "N/A"),
            "last_close": ind_h1.get("last_close", "N/A")
        }).content

    try:
        raw_response = call_llm()
        identified_trend = parse_trend_output(raw_response)
        logger.info(f"Identified Macro Trend: {identified_trend} (Raw: {raw_response.strip()[:40]})")
        return {
            "macro_trend_h1": identified_trend,
            "execution_logs": [f"Macro analysis finalized: {identified_trend}"]
        }
    except Exception as e:
        logger.error(f"H1 Trend Agent failed: {str(e)}", exc_info=True)
        return {
            "macro_trend_h1": "SIDEWAYS",
            "execution_logs": [f"Macro analysis failed with error: {str(e)}. Fallback to SIDEWAYS."]
        }