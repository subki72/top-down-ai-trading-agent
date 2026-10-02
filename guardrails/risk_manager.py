import re
from typing import Optional, Tuple, Dict, Any
from state import TradingState
from config.settings import (
    MIN_RR_RATIO,
    ACCOUNT_EQUITY,
    MAX_RISK_PER_TRADE_PCT,
    MAX_CAPITAL_ALLOCATION_PCT,
    DEFAULT_LEVERAGE,
)
from config.logger import setup_logger

logger = setup_logger("risk_manager")

def safe_extract_price(label: str, text: str) -> Optional[float]:
    """
    Robust price extraction from LLM unstructured text.
    Handles variations like:
      - 'ENTRY: 350.25'
      - 'Entry Price = $350.25'
      - 'SL: 340,50'
      - 'TP - 380.0'
    """
    if not text:
        return None

    pattern = rf'{label}\s*(?:PRICE)?\s*[:=-]?\s*\$?\s*([\d,]+(?:\.\d+)?)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            cleaned = match.group(1).replace(",", "")
            return float(cleaned)
        except ValueError:
            return None
    return None

def calculate_position_sizing(
    entry: float,
    sl: float,
    tp: float,
    equity: float = ACCOUNT_EQUITY,
    max_risk_pct: float = MAX_RISK_PER_TRADE_PCT,
    max_alloc_pct: float = MAX_CAPITAL_ALLOCATION_PCT,
    leverage: float = DEFAULT_LEVERAGE,
) -> Dict[str, float]:
    """
    Calculates exact position sizing and dollar risk based on fixed fractional risk.
    """
    risk_per_unit = abs(entry - sl)
    reward_per_unit = abs(tp - entry)
    
    if risk_per_unit <= 0 or entry <= 0:
        return {
            "position_size_tokens": 0.0,
            "position_size_usd": 0.0,
            "risk_usd": 0.0,
            "reward_usd": 0.0,
        }

    # Dollar amount willing to lose on this trade
    max_risk_dollars = (max_risk_pct / 100.0) * equity
    units = max_risk_dollars / risk_per_unit
    position_usd = units * entry

    # Cap position size by portfolio allocation limits
    max_capital_allowed = (max_alloc_pct / 100.0) * equity * leverage
    if position_usd > max_capital_allowed:
        position_usd = max_capital_allowed
        units = position_usd / entry

    actual_risk_usd = units * risk_per_unit
    actual_reward_usd = units * reward_per_unit

    return {
        "position_size_tokens": round(units, 4),
        "position_size_usd": round(position_usd, 2),
        "risk_usd": round(actual_risk_usd, 2),
        "reward_usd": round(actual_reward_usd, 2),
    }

def validate_directional_levels(
    macro_trend: str,
    entry: float,
    sl: float,
    tp: float
) -> Tuple[bool, str]:
    """
    Validates whether the stop loss and take profit make geometric and financial sense
    for the identified trend direction.
    """
    trend_upper = (macro_trend or "").upper()
    
    if trend_upper == "BULLISH":
        if sl >= entry:
            return False, f"Invalid Long geometry: SL ({sl}) must be strictly below Entry ({entry})"
        if tp <= entry:
            return False, f"Invalid Long geometry: TP ({tp}) must be strictly above Entry ({entry})"
    elif trend_upper == "BEARISH":
        if sl <= entry:
            return False, f"Invalid Short geometry: SL ({sl}) must be strictly above Entry ({entry})"
        if tp >= entry:
            return False, f"Invalid Short geometry: TP ({tp}) must be strictly below Entry ({entry})"
    else:
        # Non-directional or unspecified; fallback to standard positive distance
        if sl == entry or tp == entry:
            return False, "SL or TP cannot be identical to Entry price"

    return True, "Valid price geometry"

def validate_risk_reward(state: TradingState) -> Dict[str, Any]:
    """
    Deterministic risk guardrail:
    1. Extracts numerical trade parameters.
    2. Validates directional sanity (SL vs Entry vs TP).
    3. Calculates strict Risk-to-Reward ratio.
    4. Computes disciplined position sizing and capital allocation.
    """
    logger.info("Evaluating trade feasibility, price structure, and position sizing...")
    signal = state.get('trigger_m5', '')
    macro_trend = state.get('macro_trend_h1', 'SIDEWAYS')
    
    try:
        entry = safe_extract_price('ENTRY', signal)
        sl = safe_extract_price('SL', signal)
        tp = safe_extract_price('TP', signal)
        
        if entry is None or sl is None or tp is None:
            logger.warning("AI did not provide valid Entry/SL/TP values.")
            return {
                "is_risk_reward_valid": False,
                "rr_ratio": 0.0,
                "entry_price": None,
                "stop_loss": None,
                "take_profit": None,
                "position_size_usd": 0.0,
                "position_size_tokens": 0.0,
                "risk_usd": 0.0,
                "reward_usd": 0.0,
                "risk_rejection_reason": "MISSING_PRICE_DATA",
                "final_action": "REJECT_INVALID_FORMAT",
                "execution_logs": ["Risk guardrail rejected: Missing or unparseable price levels from AI"]
            }

        # Validate geometry against trend
        is_geo_valid, geo_reason = validate_directional_levels(macro_trend, entry, sl, tp)
        if not is_geo_valid:
            logger.warning(f"Directional check failed: {geo_reason}")
            return {
                "is_risk_reward_valid": False,
                "rr_ratio": 0.0,
                "entry_price": entry,
                "stop_loss": sl,
                "take_profit": tp,
                "position_size_usd": 0.0,
                "position_size_tokens": 0.0,
                "risk_usd": 0.0,
                "reward_usd": 0.0,
                "risk_rejection_reason": geo_reason,
                "final_action": "REJECT_INVALID_GEOMETRY",
                "execution_logs": [f"Risk guardrail rejected: {geo_reason}"]
            }

        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = round(reward / risk, 2) if risk > 0 else 0.0
        
        is_valid = rr_ratio >= MIN_RR_RATIO
        action = "EXECUTE_TRADE" if is_valid else "REJECT_BAD_RR"
        rejection_reason = "" if is_valid else f"RR 1:{rr_ratio} is below required minimum 1:{MIN_RR_RATIO}"
        
        sizing = calculate_position_sizing(entry, sl, tp)

        logger.info(
            f"Risk Check: RR 1:{rr_ratio} (Min: 1:{MIN_RR_RATIO}) | "
            f"Entry: {entry}, SL: {sl}, TP: {tp} | "
            f"Position: {sizing['position_size_tokens']} tokens (${sizing['position_size_usd']}) | Action: {action}"
        )
        
        return {
            "is_risk_reward_valid": is_valid, 
            "rr_ratio": rr_ratio, 
            "entry_price": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "position_size_usd": sizing["position_size_usd"],
            "position_size_tokens": sizing["position_size_tokens"],
            "risk_usd": sizing["risk_usd"],
            "reward_usd": sizing["reward_usd"],
            "risk_rejection_reason": rejection_reason,
            "final_action": action, 
            "execution_logs": [
                f"Risk analysis finalized: {action} (RR: 1:{rr_ratio}, Pos: ${sizing['position_size_usd']})"
            ]
        }
        
    except Exception as e:
        logger.error(f"Critical error in risk calculation: {str(e)}", exc_info=True)
        return {
            "is_risk_reward_valid": False, 
            "rr_ratio": 0.0, 
            "entry_price": None,
            "stop_loss": None,
            "take_profit": None,
            "position_size_usd": 0.0,
            "position_size_tokens": 0.0,
            "risk_usd": 0.0,
            "reward_usd": 0.0,
            "risk_rejection_reason": f"INTERNAL_ERROR: {str(e)}",
            "final_action": "CALCULATION_ERROR", 
            "execution_logs": [f"Risk guardrail critical error: {str(e)}"]
        }