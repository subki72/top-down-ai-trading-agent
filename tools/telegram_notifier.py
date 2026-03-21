import requests
from state import TradingState
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_report(state: TradingState):
    """
    Dispatches the final trading state and decision to the user via Telegram.
    Includes dynamic formatting to handle skipped execution paths.
    """
    print("[TELEGRAM] Dispatching executive report...")
    
    asset = state['asset_pair']
    action = state['final_action']
    rr_ratio = state['rr_ratio']
    trend = state['macro_trend_h1']
    
    # Dynamic handling for bypassed nodes
    m15_status = state['micro_signal_m15'] if state['micro_signal_m15'] != "" else "SKIPPED (No Pattern)"
    m5_trigger = state['trigger_m5'] if state['trigger_m5'] != "" else "SKIPPED (No Trigger)"
    
    report = (
        f"AI TRADING REPORT: {asset}\n"
        f"---------------------------\n"
        f"H1 Trend: {trend}\n"
        f"M15 Pattern: {m15_status}\n"
        f"M5 Trigger: {m5_trigger}\n"
        f"Risk/Reward Ratio: 1:{rr_ratio}\n"
        f"FINAL DECISION: {action}\n"
        f"---------------------------"
    )

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": report,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return {"execution_logs": ["Telegram report successfully dispatched"]}
    except Exception as e:
        print(f"[ERROR] Telegram delivery failed: {str(e)}")
        return {"execution_logs": [f"Telegram notification error: {str(e)}"]}