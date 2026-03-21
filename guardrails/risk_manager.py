import re
from state import TradingState
from config.settings import MIN_RR_RATIO

def validate_risk_reward(state: TradingState):
    """
    Parses the entry trigger and calculates the mathematical Risk-to-Reward ratio.
    Ensures the trade meets the minimum threshold defined in settings.
    """
    print("[RISK_MANAGER] Evaluating trade feasibility...")
    signal = state['trigger_m5']
    
    try:
        # Extracting numerical values using regular expressions
        entry = float(re.search(r'ENTRY:\s*([\d.]+)', signal).group(1))
        sl = float(re.search(r'SL:\s*([\d.]+)', signal).group(1))
        tp = float(re.search(r'TP:\s*([\d.]+)', signal).group(1))
        
        # Calculating absolute distance for risk and reward
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        
        # Calculating the ratio (Reward / Risk)
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0
        
        # Validation against the global threshold
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
            "execution_logs": ["Risk guardrail error: Invalid signal format"]
        }