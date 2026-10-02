import os
import sys
import uuid
from agent_graph import trading_firm
from config.settings import (
    GROQ_API_KEY,
    SYMBOL,
    validate_environment,
    ACCOUNT_EQUITY
)
from config.logger import setup_logger

logger = setup_logger("main")

def run_trading_session():
    session_id = str(uuid.uuid4())[:8]
    logger.info(f"=== SYSTEM BOOT: AUTOMATED TRADING FIRM [Session ID: {session_id}] ===")
    
    # 1. Startup Environment & Credential Validation
    missing_vars = validate_environment(require_telegram=False, require_supabase=False)
    if missing_vars:
        logger.critical(f"Startup aborted! Missing required environment variables: {missing_vars}")
        sys.exit(1)

    if GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY

    target_coin = os.environ.get("COIN_SYMBOL", SYMBOL)
    target_price = os.environ.get("ENTRY_PRICE", "0")
    
    logger.info(f"Target Asset: {target_coin} | Account Equity: ${ACCOUNT_EQUITY:,.2f}")
    if target_price != "0":
        logger.info(f"Target Entry Price Override: {target_price}")

    # 2. Initial State Setup
    initial_context = {
        "asset_pair": target_coin, 
        "data_h1_raw": "",
        "data_m15_raw": "",
        "data_m5_raw": "",
        "macro_trend_h1": "",
        "is_m15_setup_valid": False,
        "micro_signal_m15": "",
        "trigger_m5": "",
        
        # Risk & Capital Management
        "is_risk_reward_valid": False,
        "rr_ratio": 0.0,
        "entry_price": None,
        "stop_loss": None,
        "take_profit": None,
        "position_size_usd": 0.0,
        "position_size_tokens": 0.0,
        "risk_usd": 0.0,
        "reward_usd": 0.0,
        "risk_rejection_reason": "",
        
        "final_action": "IDLE",
        "indicators": {},
        "execution_logs": [f"Session {session_id} initiated for {target_coin}"]
    }

    try:
        final_state = trading_firm.invoke(initial_context)
        
        logger.info("=" * 50)
        logger.info(f"TRADING SESSION {session_id} COMPLETE")
        logger.info(f"Decision: {final_state.get('final_action')}")
        logger.info(f"Risk/Reward: 1:{final_state.get('rr_ratio', 0.0)}")
        if final_state.get("position_size_usd", 0.0) > 0:
            logger.info(
                f"Position Size: ${final_state.get('position_size_usd')} "
                f"({final_state.get('position_size_tokens')} tokens)"
            )
            logger.info(f"Dollar Risk: ${final_state.get('risk_usd')} | Target Reward: ${final_state.get('reward_usd')}")
        logger.info("=" * 50)
        return final_state
        
    except Exception as error:
        logger.critical(f"Critical execution failure: {str(error)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_trading_session()