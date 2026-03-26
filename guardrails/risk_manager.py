import re
from state import TradingState
from config.settings import MIN_RR_RATIO

def safe_extract_price(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return float(match.group(1)) if match else None

def validate_risk_reward(state: TradingState):
    print("[RISK_MANAGER] Evaluating trade feasibility...")
    signal = state['trigger_m5']
    
    try:
        entry = safe_extract_price(r'ENTRY\s*[:=-]?\s*([\d.]+)', signal)
        sl = safe_extract_price(r'SL\s*[:=-]?\s*([\d.]+)', signal)
        tp = safe_extract_price(r'TP\s*[:=-]?\s*([\d.]+)', signal)
        
        if entry is None or sl is None or tp is None:
            print("[RISK_MANAGER] Warning: AI did not provide clear Entry/SL/TP values.")
            return {
                "is_risk_reward_valid": False,
                "rr_ratio": 0.0,
                "final_action": "REJECT_INVALID_FORMAT",
                "execution_logs": ["Risk guardrail rejected: Missing price data from AI"]
            }
        
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0
        
        is_valid = rr_ratio >= MIN_RR_RATIO
        action = "EXECUTE_TRADE" if is_valid else "REJECT_BAD_RR"
        
        print(f"[RISK_MANAGER] Calculation: RR 1:{rr_ratio} | Required: 1:{MIN_RR_RATIO}")
        
        return {
            "is_risk_reward_valid": is_valid, 
            "rr_ratio": rr_ratio, 
            "final_action": action, 
            "execution_logs": [f"Risk analysis finalized: {action} (RR: {rr_ratio})"]
        }
        
    except Exception as e:
        print(f"[ERROR] Risk calculation failed: {str(e)}")
        return {
            "is_risk_reward_valid": False, 
            "rr_ratio": 0.0, 
            "final_action": "CALCULATION_ERROR", 
            "execution_logs": [f"Risk guardrail critical error: {str(e)}"]
        }