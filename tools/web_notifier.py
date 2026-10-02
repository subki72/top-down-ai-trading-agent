from state import TradingState
from config.supabase_client import insert_trading_signal
from config.logger import setup_logger

logger = setup_logger("web_notifier")

def send_web_report(state: TradingState):
    """Send trading signal data to Supabase for the web dashboard."""
    logger.info("Publishing signal to web dashboard...")
    
    asset = state.get('asset_pair', 'N/A')
    action = state.get('final_action', 'IDLE')
    rr_ratio = state.get('rr_ratio', 0.0)
    trend = state.get('macro_trend_h1', 'N/A')
    m15_status = state.get('micro_signal_m15') or "SKIPPED (No Pattern)"
    m5_trigger = state.get('trigger_m5') or "SKIPPED (No Trigger)"
    
    signal_data = {
        "asset_pair": asset,
        "macro_trend": trend,
        "micro_signal": m15_status,
        "trigger_detail": m5_trigger,
        "rr_ratio": rr_ratio,
        "final_action": action,
        "entry_price": state.get('entry_price'),
        "stop_loss": state.get('stop_loss'),
        "take_profit": state.get('take_profit'),
        "position_size_usd": state.get('position_size_usd', 0.0),
        "risk_usd": state.get('risk_usd', 0.0),
        "reward_usd": state.get('reward_usd', 0.0),
        "execution_logs": state.get('execution_logs', [])
    }
    
    try:
        result = insert_trading_signal(signal_data)
        if result:
            logger.info("Signal published to dashboard successfully")
            return {"execution_logs": ["Web dashboard signal published"]}
        else:
            logger.warning("Signal publish skipped or returned no result")
            return {"execution_logs": ["Web dashboard publish skipped (not configured)"]}
    except Exception as e:
        logger.error(f"Web dashboard publish failed: {str(e)}", exc_info=True)
        return {"execution_logs": [f"Web dashboard error: {str(e)}"]}
