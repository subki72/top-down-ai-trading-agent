import re
from typing import Tuple
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState
from config.settings import MODEL_ANALYST, API_TIMEOUT_SECONDS
from config.logger import setup_logger
from tools.resilience import retry_with_backoff

logger = setup_logger("pattern_agent")

def parse_pattern_output(raw_text: str) -> Tuple[bool, str]:
    """
    Robustly parses setup validation from LLM output.
    Handles formats like:
      - 'VALID - Bull Flag - Retest of EMA 21'
      - '[VALID] - Order Block - Clean FVG filled'
      - '**VALID** - Bullish Engulfing'
      - 'INVALID - No clear pattern'
    """
    if not raw_text:
        return False, "INVALID - Empty response"

    cleaned = raw_text.strip().replace("*", "").replace("#", "")
    
    # Check for VALID vs INVALID
    # Match [VALID] or VALID at the beginning or as primary verdict
    is_invalid_match = re.search(r'\bINVALID\b', cleaned, re.IGNORECASE)
    is_valid_match = re.search(r'\bVALID\b', cleaned, re.IGNORECASE)

    if is_valid_match and not is_invalid_match:
        return True, cleaned
    elif is_invalid_match and not is_valid_match:
        return False, cleaned
    elif is_valid_match and is_invalid_match:
        # If both appear (e.g. "Result: INVALID (was previously VALID)"), check which appears first
        if is_valid_match.start() < is_invalid_match.start():
            return True, cleaned
        return False, cleaned

    logger.warning(f"Could not determine validity from text: '{raw_text[:50]}'. Marking INVALID.")
    return False, cleaned

def analyze_market_structure_m15(state: TradingState):
    asset = state.get('asset_pair', 'UNKNOWN')
    trend = state.get('macro_trend_h1', 'SIDEWAYS')
    raw_data = state.get('data_m15_raw', '')
    ind_m15 = state.get('indicators', {}).get('M15', {})
    
    logger.info(f"Searching for {trend} setups on {asset} M15 timeframe...")

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
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def call_llm():
        llm = ChatGroq(
            temperature=0,
            model_name=MODEL_ANALYST,
            request_timeout=API_TIMEOUT_SECONDS
        )
        return (prompt | llm).invoke({
            "asset": asset, 
            "trend": trend, 
            "raw_data": raw_data,
            "ema_13": ind_m15.get("ema_13", "N/A"),
            "ema_21": ind_m15.get("ema_21", "N/A"),
            "rsi": ind_m15.get("rsi", "N/A"),
            "macd": ind_m15.get("macd_hist", "N/A")
        }).content

    try:
        raw_response = call_llm()
        is_valid, parsed_signal = parse_pattern_output(raw_response)
        logger.info(f"M15 Setup Validation: {is_valid} | Signal: {parsed_signal}")
        return {
            "is_m15_setup_valid": is_valid,
            "micro_signal_m15": parsed_signal,
            "execution_logs": [f"M15 setup analysis: {parsed_signal}"]
        }
    except Exception as e:
        logger.error(f"M15 Analyst Agent failed: {str(e)}", exc_info=True)
        return {
            "is_m15_setup_valid": False,
            "micro_signal_m15": f"INVALID - Error: {str(e)}",
            "execution_logs": [f"M15 setup analysis error: {str(e)}"]
        }