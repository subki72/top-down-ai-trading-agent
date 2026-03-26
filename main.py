import os
import sys 
from agent_graph import trading_firm
from config.settings import GROQ_API_KEY, SYMBOL

def run_trading_session():
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    target_coin = os.environ.get("COIN_SYMBOL", SYMBOL)
    target_price = os.environ.get("ENTRY_PRICE", "0")
    
    print("-" * 45)
    print(f"SYSTEM BOOT: AUTOMATED TRADING FIRM ({target_coin})") 
    if target_price != "0":
        print(f"TARGET ENTRY PRICE: {target_price}")
    print("-" * 45)

    initial_context = {
        "asset_pair": target_coin, 
        "data_h1_raw": "",
        "data_m15_raw": "",
        "data_m5_raw": "",
        "macro_trend_h1": "",
        "is_m15_setup_valid": False,
        "micro_signal_m15": "",
        "trigger_m5": "",
        "is_risk_reward_valid": False,
        "rr_ratio": 0.0,
        "final_action": "IDLE",
        "indicators": {},
        "execution_logs": [f"Session initiated via main.py for {target_coin}"]
    }

    try:
        final_state = trading_firm.invoke(initial_context)
        
        print("\n" + "=" * 45)
        print(f"SESSION COMPLETE")
        print(f"Decision: {final_state['final_action']}")
        print(f"RR Ratio: 1:{final_state['rr_ratio']}")
        print("=" * 45)
        
    except Exception as error:
        print(f"[CRITICAL_FAILURE] Execution interrupted: {str(error)}")
        sys.exit(1)

if __name__ == "__main__":
    run_trading_session()