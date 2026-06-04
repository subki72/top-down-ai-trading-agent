from state import TradingState
from config.supabase_client import insert_trading_signal

def send_web_report(state: TradingState):
    """Send trading signal data to Supabase for the web dashboard."""
    print("[WEB_DISPATCHER] Publishing signal to web dashboard...")
    
    asset = state['asset_pair']
    action = state['final_action']
    rr_ratio = state['rr_ratio']
    trend = state['macro_trend_h1']
    m15_status = state['micro_signal_m15'] if state['micro_signal_m15'] != "" else "SKIPPED (No Pattern)"
    m5_trigger = state['trigger_m5'] if state['trigger_m5'] != "" else "SKIPPED (No Trigger)"
    
    signal_data = {
        "asset_pair": asset,
        "macro_trend": trend,
        "micro_signal": m15_status,
        "trigger_detail": m5_trigger,
        "rr_ratio": rr_ratio,
        "final_action": action,
        "execution_logs": state.get('execution_logs', [])
    }
    
    try:
        result = insert_trading_signal(signal_data)
        if result:
            print("[WEB_DISPATCHER] Signal published to dashboard successfully")
            return {"execution_logs": ["Web dashboard signal published"]}
        else:
            print("[WEB_DISPATCHER] Warning: Signal publish returned no result")
            return {"execution_logs": ["Web dashboard publish warning: no result"]}
    except Exception as e:
        print(f"[ERROR] Web dashboard publish failed: {str(e)}")
        return {"execution_logs": [f"Web dashboard error: {str(e)}"]}
