import requests
from state import TradingState
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_report(state: TradingState):
    print("[TELEGRAM] Dispatching executive report...")
    
    asset = state['asset_pair']
    action = state['final_action']
    rr_ratio = state['rr_ratio']
    trend = state['macro_trend_h1']
    
    m15_status = state['micro_signal_m15'] if state['micro_signal_m15'] != "" else "SKIPPED (No Pattern)"
    m5_trigger = state['trigger_m5'] if state['trigger_m5'] != "" else "SKIPPED (No Trigger)"
    
    report = (
        f"<b>AI TRADING REPORT: {asset}</b>\n"
        f"---------------------------\n"
        f"<b>H1 Trend:</b> {trend}\n"
        f"<b>M15 Pattern:</b> {m15_status}\n"
        f"<b>M5 Trigger:</b> {m5_trigger}\n"
        f"<b>Risk/Reward Ratio:</b> 1:{rr_ratio}\n"
        f"<b>FINAL DECISION:</b> {action}\n"
        f"---------------------------"
    )

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": report,
        "parse_mode": "HTML" 
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return {"execution_logs": ["Telegram report successfully dispatched"]}
    except Exception as e:
        print(f"[ERROR] Telegram delivery failed: {str(e)}")
        return {"execution_logs": [f"Telegram notification error: {str(e)}"]}